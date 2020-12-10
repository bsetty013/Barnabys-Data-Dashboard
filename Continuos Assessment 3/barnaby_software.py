""" BARNABY SOFTWARE APPLICATION """
import csv
from statistics import mean
from datetime import datetime, timedelta
import random
from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt


APP = Flask(__name__)

#Module Variables

#Constants
BREW_STAGES = ["Fermentation", "Conditioning",
               "Bottling and Labelling"]
#Tank Names
TANKS = ["Albert", "Brigadier", "Camilla", "Dylon", "Emily",
         "Florence", "Gertrude", "Harry", "R2D2"]


#Dictionary Storing Info about Tanks
brewer_tanks = {
    "Albert": {"Volume": 1000, "Capabilities": ["Fermenter", "Conditioner"],
               "Batch_Content": "Nothing", "Activity_Status": "Nothing"},
    "Brigadier": {"Volume": 800, "Capabilities": ["Fermenter", "Conditioner"],
                  "Batch_Content": "Nothing", "Activity_Status": "Nothing"},
    "Camilla": {"Volume": 1000, "Capabilities": ["Fermenter", "Conditioner"],
                "Batch_Content": "Nothing", "Activity_Status": "Nothing"},
    "Dylon": {"Volume": 800, "Capabilities": ["Fermenter", "Conditioner", ],
              "Batch_Content": "Nothing", "Activity_Status": "Nothing"},
    "Emily": {"Volume": 1000, "Capabilities": ["Fermenter", "Conditioner"],
              "Batch_Content": "Nothing", "Activity_Status": "Nothing"},
    "Florence": {"Volume": 800, "Capabilities": ["Fermenter", "Conditioner"],
                 "Batch_Content": "Nothing", "Activity_Status": "Nothing"},
    "Gertrude": {"Volume": 680, "Capabilities": ["Conditioner"],
                 "Batch_Content": "Nothing", "Activity_Status": "Nothing"},
    "Harry": {"Volume": 680, "Capabilities": ["Conditioner"],
              "Batch_Content": "Nothing", "Activity_Status": "Nothing"},
    "R2D2": {"Volume": 800, "Capabilities": ["Fermenter"],
             "Batch_Content": "Nothing", "Activity_Status": "Nothing"}
    }


#Info about current batches being brewed
current_brewings = []

#Bottles in each recipe ready for delivery
delivery_information = {
    "Organic Red Helles": 0,
    "Organic Pilsner": 0,
    "Organic Dunkel": 0
    }


##Home Page##
@APP.route("/", methods=["GET", "POST"])
def home_page() -> str:
    """This function returns a singular
       html template. This template enables
       the user to view the home page. This
       is the centre of the program and
       where you can access all the various
       different parts of the program
       through the buttons provided."""
    return render_template("home.html")


##Opening Pages##

@APP.route("/add_row", methods=["GET", "POST"])
def add_row() -> str:
    """This function returns a singlular html
       template. This produces the user interface
       where several input fields are created so
       users can input the relevant information
       to create an invoice."""
    return render_template("add_row.html")



@APP.route("/prediction_input", methods=["GET", "POST"])
def prediction_input() -> str:
    """This function passes two lists two a singular html
       tempalate which is returned at the end of the function.
       This template allows the user interface to display two drop
       down menu's which the user can select from, so the program
       can make a prediction."""
    recipe_list = ["Organic Red Helles", "Organic Pilsner",
                   "Organic Dunkel"]
    month_list = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct"]
    return render_template("prediction_input.html", recipes=recipe_list,
                           months=month_list)


@APP.route("/projection_input", methods=["GET", "POST"])
def projections_input() -> str:
    """This function passes a list to a singular
       html template which is returned at the end of the
       function. This template allows the user interface display
       a drop down menu where the user can select from one of
       the recipes. Based on this input a scatter graph is produced
       with a line of best fit."""
    recipe_list = ["Organic Red Helles", "Organic Pilsner",
                   "Organic Dunkel"]
    return render_template("projection_input.html", recipes=recipe_list)

@APP.route("/start_brew", methods=["GET", "POST"])
def start_brew() -> str:
    """This function passes a list to a singular html
       template which is returned at the end of the function.
       This template allows the user interface to display a
       drop down menu where the user can select from one of
       the recipes. Based on this input a message is produced
       about whether a brew has started or not."""
    recipe_names = ["Organic Red Helles", "Organic Pilsner",
                    "Organic Dunkel"]
    return render_template("start_brew.html",
                           recipes=recipe_names,
                           tank_options=TANKS)

@APP.route("/viewtank_input", methods=["GET", "POST"])
def viewtank_input() -> str:
    """This function passes a list to a singular html
       template which is returned at the end of the
       function. This template allows the user interface
       to display a drop down menu where the user can
       select from one of the existing tanks. Based
       on the tank chosen by the user the information
       about the tank inputted by the user will be
       outputted onto the user interface."""
    tank_list = ["Albert", "Brigadier", "Camilla",
                 "Dylon", "Emily", "Florence",
                 "Gertrude", "Harry", "R2D2"]
    return render_template("viewtank_input.html",
                           tanks=tank_list)

@APP.route("/view_batches", methods=["GET", "POST"])
def view_batches() -> str:
    """This function passes two lists to a
       html template. The template allows the
       user interface to display two drop down
       menu's which the user can select from.
       Based on these inputs the program can
       move a batch from stage of the brewing
       process to another.The template allows
       the user interface to display details
       about all the current batches that are
       being brewed."""
    tank_possibilities = ["Albert", "Brigadier", "Camilla", "Dylon", "Emily",
                          "Florence", "Gertrude", "Harry", "R2D2",
                          "No Tank Needed"]
    return render_template("view_batches.html",
                           batch_output=current_brewings,
                           tank_options=tank_possibilities)

@APP.route("/progress_confirm", methods=["GET", "POST"])
def progress_confirm() -> str:
    """This function attempts to move a batch chosen
       by the user onto the next brewing stage. A message
       is returned and passed to the html template about
       whether the stage progression was successful. The html
       template allows the user interface to display a message
       to the user about whether the stage progression was
       successful or not."""
    message_display = "Batch is not being Currently Brewed"
    #Catches batch number user has entered on UI
    user_batch = request.args.get("move_number")
    #Catches tank user has entered on UI
    next_tank = request.args.get("tank_choice")
    print(user_batch)
    for brew_section in current_brewings:
        if brew_section[0] == user_batch:
            #Finding the list in current_brewings where the batch
            #the user is interested in is stored
            batch_index = current_brewings.index(brew_section)
            message_display = stage_progresser(batch_index, next_tank)
            break

    return render_template("progress_confirm.html",
                           display_message=message_display)


@APP.route("/view_delivery", methods=["GET", "POST"])
def view_delivery() -> str:
    """This function appends the amount of bottles
       available for delivery for each recipe in a list
       from the dictionary. These are then passed to a
       html template that is returned at the end of the
       function. The html template allows the user to
       view all the bottles available for delivery
       for each beer type. This is displayed in a
       table on the user interface."""
    #List with amount of bottles ready for delivery for each lsit
    delivery_amounts = []
    delivery_amounts.append(delivery_information["Organic Red Helles"])
    delivery_amounts.append(delivery_information["Organic Pilsner"])
    delivery_amounts.append(delivery_information["Organic Dunkel"])
    return render_template("view_delivery.html",
                           delivery_displays=delivery_amounts)




##Significant Processing Methods##

def data_add(invoice_details):
    """This function takes a single argument
       which is a list. This list contains
       all the details a user has entered to
       add an invoice to the CSV file. The
       elements in this list will be written
       to the CSV file."""
    with open("beer_data.csv", "a") as data_file:
        writer = csv.writer(data_file)
        writer.writerow(invoice_details)
    data_file.close()



def dictionary_formation():
    """This forms a dictionary that contains
       all the sales data from the CSV file.
       The function reads every row in the file
       and stores it in a dictionary in sales_data.
       Every column in the line of the CSV file will
       be stored under a key value in a dictionary in
       sales_data.At the end of the function the
       dictionary that is formed is returned."""
    sales_data = {}
    with open('beer_data.csv', "r") as data_file:
        file_contents = csv.reader(data_file, delimiter=',')
        #Value of lines_read used as key value for each dictionary
        #in sales_data
        lines_read = 1
        for line in file_contents:
            if lines_read == 1:
                lines_read = lines_read + 1
            else:
                #Stores each column in row as key value in dictionary
                sales_data[str(lines_read)] = {
                    "invoice_number": line[0],
                    "customer": line[1],
                    "date_required": line[2],
                    "recipe": line[3],
                    "gyle_number": line[4],
                    "quantity_ordered": int(line[5])
                }
                lines_read = lines_read + 1
    data_file.close()
    return sales_data


def amount_gathering(user_recipe):
    """This gathers the amount of bottles
       every month for a recipe entered by the
       user. The function reads every line the
       CSV file that has the recipe that is
       equivalent to the recipe entered by the
       user. The quanitity ordered is added
       to an ongoing total that occurs for each
       month. This is then appended to a list.
       At the end of the function, a list is returned
       with a total amount of bottles for each month."""
    #Forms Dictionary
    sales_stats = dictionary_formation()
    amount_list = []
    month_list = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May",
                  "Jun", "Jul", "Aug", "Sep", "Oct"]
    for month in month_list:
        bottles_amount = 0
        dicts_read = 2
        for dicts_read in sales_stats:
            analyse_dict = sales_stats[str(dicts_read)]
            if month in analyse_dict["date_required"]:
                if analyse_dict["recipe"] == user_recipe:
                    bottles_amount += analyse_dict["quantity_ordered"]
        amount_list.append(bottles_amount)
    return amount_list


def growth_calculations(user_recipe) -> int:
    """This function takes the output of amount_gathering
       and a list where there is a number assinged for each month.
       Using these two list's an average growth rate is calculated.
       In simplistic terms, this is the gradient of a line of best fit
       of a scatter graph produced between the two lists. This growth rate
       is returned at the end."""
    month_numbers = np.array([1, 2, 3, 4, 5, 6,
                              7, 8, 9, 10, 11, 12], dtype=np.float64)
    month_amounts = np.array(amount_gathering(user_recipe),
                             dtype=np.float64)
    numerator = ((mean(month_numbers) * mean(month_amounts)) -
                 (mean(month_numbers*month_amounts)))
    denominator = ((mean(month_numbers))**2) - mean(month_numbers**2)
    growth = numerator/denominator
    return growth

def conditioning_move(batch_index, next_tank, next_stage) -> str:
    """This function uses the batch number and tank entered
       by the user and uses it so the batch is moved from
       fermentation to conditioning.At the end of the function
       a string is returned consisting of a message that
       the attempted brew progress was successful."""
    #Calculating Current Date and Time
    now = datetime.now()
    start_time = now.strftime("%d/%m/%Y %H:%M:%S")
    #Calculating Estimated End Date
    end_time = now + timedelta(days=14)
    #Changing Details about the Batch
    current_brewings[batch_index][1] = start_time
    current_brewings[batch_index][4] = next_stage
    current_brewings[batch_index][5] = next_tank
    current_brewings[batch_index][6] = end_time
    #Filling New Tank
    brewer_tanks[next_tank]["Batch_Content"] = current_brewings[batch_index][0]
    brewer_tanks[next_tank]["Activity_Status"] = "Conditioning"
    fermentation_message = ("Batch currently going under "
                            +next_stage + " in " + next_tank)
    return fermentation_message


def bottling_move(batch_index, next_stage) -> str:
    """"This function moves a batch from
        conditioning to bottling and labelling.
        The function returns a string at the end
        that confirms that brew stage progression
        was successful and complete."""
    #Calculating Current Date and Time
    now = datetime.now()
    start_time = now.strftime("%d/%m/%Y %H:%M:%S")
    #Emptying Current tank
    current_tank = current_brewings[batch_index][5]
    brewer_tanks[current_tank]["Batch_Content"] = "Nothing"
    brewer_tanks[current_tank]["Activity_Status"] = "Nothing"
    #Changing Details about the Batch
    current_brewings[batch_index][1] = start_time
    current_brewings[batch_index][4] = next_stage
    current_brewings[batch_index][5] = "Nothing"
    current_brewings[batch_index][6] = "Nothing"
    bottle_message = "Batch is currently being bottled and labelled"

    batch_bottles = int(current_brewings[batch_index][3] * 2)
    batch_recipe = current_brewings[batch_index][2]
    delivery_information[batch_recipe] += batch_bottles

    return bottle_message


def stage_progresser(batch_index, next_tank) -> str:
    """This function moves a batch entered by the user
       from one brewing stage to another brewing stage.
       The function takes the batch and the tank entered by
       the user and queries this data. If this data is not
       suitable for the request they have made the function
       will return a string that states what is wrong with
       the user input. If the inputs from the user are fine
       then a function is called to move a batch to the next
       stage."""
    #Works Out What the Next Stage of the Brewing Process is
    #For that specefic batch
    current_stage = current_brewings[batch_index][4]
    next_stage_index = BREW_STAGES.index(current_stage) + 1
    next_stage = BREW_STAGES[next_stage_index]
    if next_stage == "Conditioning":
        if next_tank != "No Tank Needed":
            if "Conditioner" in brewer_tanks[next_tank]["Capabilities"]:
                #Emptying Current Tank
                current_tank = current_brewings[batch_index][5]
                brewer_tanks[current_tank]["Batch_Content"] = "Nothing"
                brewer_tanks[current_tank]["Activity_Status"] = "Nothing"
                if brewer_tanks[next_tank]["Batch_Content"] == "Nothing":
                    if brewer_tanks[next_tank]["Volume"] >= current_brewings[batch_index][3]:
                        tank_message = conditioning_move(batch_index, next_tank, next_stage)
                    else:
                        tank_message = ("This Tank does not have a large " +
                                        "enough capacity for this batch")
                        #Filling Tank Back UP
                        batch_number = current_brewings[batch_index][0]
                        brewer_tanks[current_tank]["Batch_Content"] = batch_number
                        brewer_tanks[current_tank]["Activity_Status"] = current_stage
                else:
                    tank_message = "This Tank is Currently Full"
                    #Filling Tank Back Up
                    brewer_tanks[current_tank]["Batch_Content"] = current_brewings[batch_index][0]
                    brewer_tanks[current_tank]["Activity_Status"] = current_stage
            else:
                tank_message = "Tank Does Not have This Capability"
                #Filling Tank Back Up
                brewer_tanks[current_tank]["Batch_Content"] = current_brewings[batch_index][0]
                brewer_tanks[current_tank]["Activity_Status"] = current_stage
        else:
            tank_message = "A Tank is Required for this Brewing Stage"
    elif next_stage == "Bottling and Labelling":
        if next_tank == "No Tank Needed":
            tank_message = bottling_move(batch_index, next_stage)
        else:
            tank_message = "No Tank is Required for this Brewing Stage"



    return tank_message



def assign_batch_number() -> str:
    """When  a user creates a batch
       this function randomly creates a batch
       number that can be assigned to the batch.
       The function creates a list of all the batch
       numbers that have already been assigned. Then
       the function will keep randomly choosing numbers
       until a number is chosen that is not the list
       assinged_numbers."""
    valid_number = None
    assigned_numbers = []
    #Creates a list of all the currently assigned batch numbers
    for inner_list in current_brewings:
        assigned_numbers.append(inner_list[0])
    #Keeps randomly generating a number until a number is chosen
    #That is not in assigned_numbers
    while valid_number is not True:
        batch_number = random.randint(120, 300)
        if batch_number in assigned_numbers:
            batch_number = random.randint(120, 300)
        else:
            valid_number = True
    return str(batch_number)

def highest_growth_rate():
    """This function returns a list of strings
       that containg the average growth rates
       of each beer recipe. It aslo returns
       a string containing the beer recipe with
       the highest growth rate"""
    growth_mappings = {
        "Organic Red Helles": 0,
        "Organic Pilsner": 0,
        "Organic Dunkel": 0
        }
    rate_strings = []
    #Growth Rate of Organic Red Helles
    growth_rate = int(growth_calculations("Organic Red Helles"))
    growth_mappings["Organic Red Helles"] = growth_rate
    rate_strings.append("The current growth rate for Organic Red " +
                        "Helles is: " + str(growth_rate) +
                        " bottles per month")
    #Growth Rate of Organic Pilsner
    growth_rate = int(growth_calculations("Organic Pilsner"))
    growth_mappings["Organic Pilsner"] = growth_rate
    rate_strings.append("The current growth rate for Organic " +
                        "Pilsner is: " + str(growth_rate) +
                        " bottles per month")
    #Growth Rate of Organic Dunkel
    growth_rate = int(growth_calculations("Organic Dunkel"))
    growth_mappings["Organic Dunkel"] = growth_rate
    rate_strings.append("The current growth rate for Organic " +
                        "Dunkel is: " + str(growth_rate) +
                        " bottles per month")
    #Finds largest key value in dictionary
    most_demand_recipe = max(growth_mappings, key=growth_mappings.get)
    most_demand_string = ("Therefore the beer recipe with the highest growth" +
                          " rate currently is: " + most_demand_recipe)
    return rate_strings, most_demand_string



def tank_search():
    """This function searches for all the available tanks
       that have fermentation and conditioning capabilities. The
       function returns strings containing all the tanks that are
       availalable for fermentation and conditioning. The function
       the decides whether fermentation or conditioning is advisable
       based on the amount of available tanks and returns a boolean
       variable which states whether more brewing is advisable."""
    more_fermentation = None
    more_fermentation = None
    fermentation_tanks = []
    conditioning_tanks = []
    #Search for available tanks that can ferment
    for tank_type in TANKS:
        if "Fermenter" in brewer_tanks[tank_type]["Capabilities"]:
            if brewer_tanks[tank_type]["Activity_Status"] == "Nothing":
                fermentation_tanks.append(tank_type)
    #Search for available tanks that can condition
    for each_tank in TANKS:
        if "Conditioner" in brewer_tanks[each_tank]["Capabilities"]:
            if brewer_tanks[tank_type]["Activity_Status"] == "Nothing":
                conditioning_tanks.append(each_tank)

    fermentation_string = "The current tanks available for fermentation: "
    for element in fermentation_tanks:
        fermentation_string += (" " + element)
    conditioning_string = "The current tanks available for conditioning: "
    for index in conditioning_tanks:
        conditioning_string += (" " + index)

    #Validates wether more beer should be amde
    if len(fermentation_tanks) < 2:
        fermentation_advice = ("Fermentation of new beer is not advisable " +
                               "due to the fact there are only " +
                               str(len(fermentation_tanks)) +
                               " fermentation tanks available")
        more_fermentation = False
    else:
        fermentation_advice = ("Fermentation of new beer is advisable " +
                               "due to the fact there are " +
                               str(len(fermentation_tanks)) +
                               " fermentation tanks available")
        more_fermentation = True
    if len(conditioning_tanks) < 2:
        conditioning_advice = ("Conditioning of new beer is not advisable " +
                               "due to the fact there are only " +
                               str(len(conditioning_tanks)) +
                               " conditioning tanks available")
        more_conditioning = False
    else:
        conditioning_advice = ("Conditioning of new beer is advisable " +
                               "due to the fact there are " +
                               str(len(conditioning_tanks)) +
                               " conditioning tanks available")
        more_conditioning = True

    if more_fermentation and more_conditioning:
        more_beer = True
    else:
        more_beer = False

    return (fermentation_string, conditioning_string,
            fermentation_advice, conditioning_advice,
            more_beer)


def upcoming_future_prediction(beer_recipe) -> int:
    """This function calculates the required bottles
       for the next 3 months based on one of the beer
       recipes. It calls functions from above that
       calculate the growth rate and using last months
       takings and the growth rate it calculates the
       total bottles for the next three months for a
       given recipe."""
    #Growth Rate for Recipe
    recipe_growth = growth_calculations(beer_recipe)
    #Get all of last years takings
    last_years_takings = amount_gathering(beer_recipe)
    #Get last months takings
    last_takings = last_years_takings[11]
    #Adds on to the taking using growth rate to
    #to make prediction
    first_month_total = (last_takings + recipe_growth)
    second_month_total = (last_takings +
                          (2 * recipe_growth))
    third_month_total = (last_takings +
                         (3 * recipe_growth))
    upcoming_total = (first_month_total + second_month_total +
                      third_month_total)
    return upcoming_total

def bottles_required(beer_recipe):
    """This function calculates the amount of bottles that
       still need to be made. It calculates the bottles
       needed for the next three months for a given recipe
       using the function above. Then it subtracts the bottles
       ready for delivery ,extracted for the delivery_information
       dictionary, from amount for the next three months."""
    bottles_demanded = upcoming_future_prediction(beer_recipe)
    bottles_ready = delivery_information[beer_recipe]
    if bottles_ready > bottles_demanded:
        bottles_needed = 0
    else:
        bottles_needed = bottles_demanded - bottles_ready
    return int(bottles_demanded), bottles_ready, int(bottles_needed)






##Processing User Input and UI Output##


@APP.route("/add_invoice", methods=["GET", "POST"])
def add_invoice() -> str:
    """This function adds details about a new invoice
       It catches data entered by the user on the user
       interface and stores it under variables. Then,
       all the data stored under these variables are
       appended to a list. This list is then passed to
       a function where the details in the list will be
       written to the CSV file. At the end of the function
       a singular html template is returned.This displays
       a confirmation message on the user interface that
       states that the invoice has been added to the CSV
       file. Moreover a 'HOME' button is displayed which
       allows the user to go back to the home page when the
       button is clicked."""
    invoice_details = []
    #Catching values user has entered in UI
    invoice_number = request.args.get("invoice_number")
    invoice_details.append(invoice_number)
    customer = request.args.get("customer")
    invoice_details.append(customer)
    date_required = request.args.get("date_required")
    invoice_details.append(date_required)
    recipe = request.args.get("recipe")
    invoice_details.append(recipe)
    gyle_number = request.args.get("gyle_number")
    invoice_details.append(gyle_number)
    quantity_ordered = request.args.get("quantity_ordered")
    invoice_details.append(quantity_ordered)
    #Passing list to function which writes list to CSV file
    data_add(invoice_details)
    invoice_message = "INVOICE ADDED"
    return render_template("singular_message.html",
                           user_display=invoice_message)



@APP.route("/prediction_output", methods=["GET", "POST"])
def prediction_output() -> str:
    """This function predicts the amount of bottles
       for a month next year entered by the user. It
       will also be based on the a beer recipe entered
       by the user. The function passes the growth rate
       of the recipe entered by the user and the amount
       predicted for that month entered by the user to a
       html template that is returned at the end of the
       function. The html template allows the user interface
       to display the ,growth rate of the recipe and the
       predicted amount of bottles for the month, to the
       user"""
    month_coding = {
        "Nov": 1, "Dec": 2, "Jan": 3, "Feb": 4, "Mar": 5,
        "Apr": 6, "May": 7, "Jun": 8, "Jul": 9, "Aug": 10,
        "Sep": 11, "Oct": 12
    }
    #Catches beer recipe user has entered on UI
    user_recipe = str(request.args.get("recipes"))
    #Catches month user has entered on UI
    user_month = str(request.args.get("months"))
    #Uses function to calculate growth rate through last year
    #for the beer recipe entered by the user
    growth_rate = growth_calculations(user_recipe)
    #Getting last years takings
    previous_takings = amount_gathering(user_recipe)
    #Getting last months takings
    last_taking = previous_takings[11]
    increase_amount = month_coding[user_month] * growth_rate
    #Calculates predicted amount of bottles for month entered by user
    user_amount = int(last_taking + increase_amount)
    growth_display = ("The current growth rate of " + user_recipe +
                      " is: " + str(int(growth_rate)) + "bottles per month")
    amount_display = ("The amount of bottles required in "+
                      user_month + ": "+ str(user_amount))
    return render_template("prediction_output.html"
                           , display_growth=growth_display
                           , display_amount=amount_display)



@APP.route("/projection_output", methods=["GET", "POST"])
def projection_output() -> str:
    """This function creates a scatter graph, based on a
       recipe entered by the user. Also a line of best fit
       is calculated and plotted onto the scatter graph.
       This graphical data analysis is then passed to a
       html template that is returned at the end of the
       function. The template allows the user interface
       to display the graphical data analysis produced by
       this function to the user."""
    user_recipe = request.args.get("recipes")
    #X Axis
    month_list = ["Nov 2018", "Dec 2018", "Jan 2019", "Feb 2019", "Mar 2019",
                  "Apr 2019", "May 2019", "Jun 2019", "Jul 2019", "Aug 2019",
                  "Sep 2019", "Oct 2019"]
    month_numbers = np.array([1, 2, 3, 4, 5, 6,
                              7, 8, 9, 10, 11, 12], dtype=np.float64)
    #Monthly amounts of bottles last year
    month_amounts = np.array(amount_gathering(user_recipe), dtype=np.float64)
    #Plots Graph
    plt.scatter(month_list, month_amounts, label="Bottle Amount", color="k")
    #Labels x axis
    plt.xlabel("Months")
    #Labels y axis
    plt.ylabel("Amounts")
    #Titles the graph
    plt.title("Last Year's Projections")
    #Calculates Slope of Best Fit Line
    gradient = growth_calculations(user_recipe)
    #Calculates Y-Interecept of Best Fit Line
    intercept = mean(month_amounts) - gradient*mean(month_numbers)
    best_fit = [(gradient * month)+intercept for month in month_numbers]
    #Plots Line of Best Fit
    plt.plot(month_numbers, best_fit)
    plt.legend()
    return render_template("projection_output.html", graph=plt.show())


@APP.route("/brew_process", methods=["GET", "POST"])
def brew_process() -> str:
    """This function attempts to starts a batch
        for fermentation based on details
        entered by the user. The function will return
        a string stating whether the brew startup for
        the batch was successful. This string is passed to
        a html template that is returned at the end of the
        function. The html template displays this string
        on the user interface. This allows the user to
        acknowledge whether their attempted brewing
        startup of the batch they entered was successful
        or not."""
    brew_section = []
    batch_recipe = request.args.get("recipe_ask")
    batch_tank = str(request.args.get("tank_question"))
    if brewer_tanks[batch_tank]["Activity_Status"] == "Nothing":
        if "Fermenter" in brewer_tanks[batch_tank]["Capabilities"]:
            batch_number = assign_batch_number()
            now = datetime.now()
            starting_point = now.strftime("%d/%m/%Y %H:%M:%S")
            expected_end = datetime.now() + timedelta(days=28)
            batch_amount = brewer_tanks[str(batch_tank)]["Volume"]
            #Appends info about batch being brewed in batch
            brew_section.append(batch_number)
            brew_section.append(starting_point)
            brew_section.append(batch_recipe)
            brew_section.append(int(batch_amount))
            brew_section.append("Fermentation")
            brew_section.append(str(batch_tank))
            brew_section.append(expected_end)
            current_brewings.append(brew_section)
            brewer_tanks[str(batch_tank)]["Batch_Content"] = batch_number
            brewer_tanks[str(batch_tank)]["Activity_Status"] = "Fermenting"
            brew_message = "Brew for this Batch has Started"
        else:
            brew_message = "This Tank is not Capable of this Activity"
    else:
        brew_message = "This Tank is Full"

    return render_template("singular_message.html",
                           user_display=brew_message)

#batch content activity status
@APP.route("/cancel_brew", methods=["GET", "POST"])
def cancel_brew():
    """This function cancels a brew that the user
       has created. It catches the batch number that
       the user has entered and uses this to remove the
       brew from current_brewings and empty the tanks
       the batch is stored in. At the end of the function
       a html template is returned. This states whether
       the brew has successfully cancelled."""
    brew_cancelled = False
    #Catches batch number entered by user
    cancel_batch = request.args.get("cancel_number")
    #Searches for list with the batch number entered by the user
    for inner_list in current_brewings:
        if inner_list[0] == cancel_batch:
            current_brewings.remove(inner_list)
            cancel_tank = inner_list[5]
            brewer_tanks[cancel_tank]["Batch_Content"] = "Nothing"
            brewer_tanks[cancel_tank]["Activity_Status"] = "Nothing"
            brew_cancelled = True

    if brew_cancelled:
        cancel_message = "Brew has been Cancelled"
    else:
        cancel_message = ("This batch number does not exist" +
                          " Brew has not been cancelled")

    return render_template("singular_message.html",
                           user_display=cancel_message)




@APP.route("/viewtank_output", methods=["GET", "POST"])
def viewtank_output() -> str:
    """This function takes catches the tank entered
       by the user. The function interrogates the
       dictionary with the name of the tank entered by the user
       and stores relevant information about the tank
       in a list. This list is then passed to a html
       template which is returned at the end of the
       function. The html template displays the
       interrogated information ,that was stored in the
       list, on the user interface."""
    details_output = []
    #Catches tank user has entered on UI
    user_tank = request.args.get("tank_ask")
    volume_string = ("The volume of the tank is: " +
                     str(brewer_tanks[str(user_tank)]["Volume"]))
    details_output.append(volume_string)
    capability_string = "The capabilities of this string are: "
    for capability in brewer_tanks[str(user_tank)]["Capabilities"]:
        capability_string += capability + " "
    details_output.append(capability_string)
    content_string = ("In the tank the batch currently being stored is: " +
                      str(brewer_tanks[str(user_tank)]["Batch_Content"]))
    details_output.append(content_string)
    activity_string = ("In the tank the batch is currently being: " +
                       str(brewer_tanks[str(user_tank)]["Activity_Status"]))
    details_output.append(activity_string)
    return render_template("viewtank_output.html",
                           output_details=details_output)


@APP.route("/make_first_recommendation", methods=["GET", "POST"])
def make_first_recommendation() -> str:
    """This is the first part of the recommendation to the
       user. This calls a function that searches for all
       the tanks currently available and all their capabilites.
       It then passes this information to a html template that
       is returned at the end of the function. The html template
       allows the user interface to display all the available tanks
       and makes a recommendation about whether fermentation or
       conditioning should start.If the program recommends to start
       a phase of the brewing process a 'NEXT' button is produced.
       If the program recommends to not start a 'HOME' button
       is produced."""
    available_tanks = tank_search()
    fermentation_tanks = available_tanks[0]
    conditioning_tanks = available_tanks[1]
    fermentation_advice = available_tanks[2]
    conditioning_advice = available_tanks[3]
    more_beer = available_tanks[4]
    return render_template("make_first_recommendation.html",
                           fermentation_string=fermentation_tanks,
                           conditioning_string=conditioning_tanks,
                           first_advice=fermentation_advice,
                           second_advice=conditioning_advice,
                           next_page=more_beer)


@APP.route("/make_second_recommendation", methods=["GET", "POST"])
def make_second_recommendation() -> str:
    """This is the second part of the recommendation to the
       user. This calls a function that calculates the
       average growth rates of all the recipes and appends
       them to a list. It also returns the recipe with the
       highest average growth rate. These are all passed
       to a html template that is returned at the end of
       the function. The html templates allows the user
       interface to display all the growth rates for each
       recipe and the recipe with the highest growth rate."""
    growth_rate_info = highest_growth_rate()
    rate_strings = growth_rate_info[0]
    most_demand_string = growth_rate_info[1]
    return render_template("make_second_recommendation.html",
                           display_rates=rate_strings,
                           most_demand_display=most_demand_string)

@APP.route("/make_third_recommendation", methods=["GET", "POST"])
def make_third_recommendation() -> str:
    """This function uses functions from above to calculate
       the amount of bottles needed for the next three months in each recipe,
       the amount of bottles ready for delivery for each recipe, and
       the amount of bottles needed still to be brewed. All
       this information is sent to a html template that
       is returned at the end of the function. Also the
       function calculates the recipe that needs to the
       most bottles to be made. This also returned to the html
       template. The html template allows all the information
       explained above, to be displayed on the user interface."""
    requirement_mappings = {
        "Organic Red Helles": 0,
        "Organic Pilsner": 0,
        "Organic Dunkel": 0}
    helles_info = bottles_required("Organic Red Helles")
    pilsner_info = bottles_required("Organic Pilsner")
    dunkel_info = bottles_required("Organic Dunkel")

    requirement_mappings["Organic Red Helles"] = helles_info[2]
    requirement_mappings["Organic Pilsner"] = pilsner_info[2]
    requirement_mappings["Organic Dunkel"] = dunkel_info[2]
    most_needed_recipe = max(requirement_mappings, key=requirement_mappings.get)

    return render_template("make_third_recommendation.html",
                           helles_display=helles_info,
                           pilsner_display=pilsner_info,
                           dunkel_display=dunkel_info,
                           most_needed_display=most_needed_recipe)


if __name__ == "__main__":
    APP.run(debug=True, use_reloader=True)
