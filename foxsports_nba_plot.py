import json
import requests
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go

# Player class
class Player:
    
    def __init__(self, player_dict):
        self.team = player_dict['team'] if 'team' in player_dict else ""
        self.name = player_dict['name'] if 'name' in player_dict else ""
        self.injuries = player_dict['injuries'] if 'injuries' in player_dict else []
        
    def __str__(self):
        if len(self.name) == 0:
            return "Null Player Object"
        return "{} - {}".format(self.team, self.name)

# Grabs Player Injury Information from Database
# Parameter: Player Name in String Format:
#            1) 2 words separated by a space
#            2) 1 word
# Returns: Dictionary containing Player Information
def get_player_data(input_):
    conn = sqlite3.connect("nba_player_injuries.db")
    cur = conn.cursor()
    player_name = input_.split()
    statement = """SELECT * FROM Players WHERE Name LIKE "%{}%" """.format(player_name[0])
    # If only one name is entered, it will still be searched and users will be prompt if multiple results are found
    if len(player_name) == 2:
        statement += """AND Name LIKE "%{}%" """.format(player_name[1])
        
    cur.execute(statement)
    returned_ls = cur.fetchall()
    
    # If multiple results
    if len(returned_ls) > 1:
        print("Your Search returned multiple results, please select the ID associated with the player you want.")
        counter = 0
        for item in returned_ls:
            counter += 1
            print('{}. {}'.format(counter, item[1]))
            
        input_ = input("Please choose a player by ID: ")
        while not input_.isdigit() or int(input_) < 1 or int(input_) > counter:
            input_= input("Invalid Input! Please try again: ")
        chosen_id = int(input_)
        player_id = returned_ls[chosen_id-1][0]
        player_name = returned_ls[chosen_id-1][1]
    elif len(returned_ls) == 1:
        player_id = returned_ls[0][0]
        player_name = returned_ls[0][1]
    else:
        print("Your Search did not return any results.")
        conn.close()
        return {}
    
    # Return Player Data
    statement = """SELECT p.Name, t.Name, i.Date, i.Name FROM Players AS p
                    JOIN Teams as t
                    JOIN Injuries as i
                    WHERE p.Id = {}
                    AND p.TeamId = t.Id
                    AND i.PlayerId = p.Id""".format(player_id)
    cur.execute(statement)
    returned_ls = cur.fetchall()
    player_dict = {}
    try:
        player_dict['name'] = returned_ls[0][0]
        player_dict['team'] = returned_ls[0][1]
        player_dict['injuries'] = []
        for item in returned_ls:
            temp_dict = {}
            temp_dict['date'] = item[2]
            temp_dict['injury'] = item[3]
            player_dict['injuries'].append(temp_dict)
    except Exception as e:
        print("Player {} has not sustained prior injuries.".format(player_name))
        conn.close()
        return {}
    conn.close()
    return player_dict

# Use Player Data to Plot Infographics on Plotly
# Parameter: Player Object created using data returned from get_player_data()
# Returns: nothing   
def plot(player):
    if len(player.name) < 1:
        print("="*20)
        return
    # Load Injury Dictionary
    injury_loc_dict_file = open('injury_loc_dict.json', 'r')
    injury_loc_dict = json.loads(injury_loc_dict_file.read())
    injury_keys = list(injury_loc_dict.keys())
    injury_loc_dict_file.close()
    
    # Fill Graph Data
    injury_data = []
    injury_data_unlisted = []
    loc_dict = {}
    # Add injuries to a dictionary where injuries at the same location are grouped together
    for injury in player.injuries:
        injury_name = injury['injury']
        for key in injury_keys:
            if key in injury_name.lower():
                if isinstance(injury_loc_dict[key], dict):
                    if 'right' in injury_name.lower():
                        loc_key = ' '.join(str(num) for num in injury_loc_dict[key]['r'])
                        dict_accum_helper(loc_dict, loc_key, injury_name)
                    elif 'left' in injury_name.lower():
                        loc_key = ' '.join(str(num) for num in injury_loc_dict[key]['l'])
                        dict_accum_helper(loc_dict, loc_key, injury_name)
                    else:
                        injury_data_unlisted.append(injury_name)
                else:
                    loc_key = ' '.join(str(num) for num in injury_loc_dict[key])
                    dict_accum_helper(loc_dict, loc_key, injury_name)
                break
    # Create Trace for each injury location
    for key in list(loc_dict.keys()):
        key_ls = key.split()
        if '-' in key:
            loc_x = [-1, float(key_ls[0])]
            textposition='center left'
        else:
            loc_x = [1, float(key_ls[0])]
            textposition='center right'
        loc_y = [float(key_ls[1]) for i in range(2)]
        trace = go.Scatter(
            x=loc_x,
            y=loc_y,
            mode='lines+markers+text',
            text=["<br>" * (len(loc_dict[key])-1) + "<br>".join(loc_dict[key])],
            textposition=textposition,
            line=dict(
                width=2,
                color='rgb(255, 204, 0)',
            ),
            showlegend = False,
            hoverinfo= 'none'
            )
        injury_data.append(trace)
    # Append unlisted injury
    trace_unlisted = go.Scatter(
            x=[-2.4],
            y=[2.5],
            mode='markers+text',
            text=["<br>" * (len(injury_data_unlisted)+1) + "<b>Vague Injuries: </b><br>"+"<br>".join(injury_data_unlisted)],
            textposition='center right',
            line=dict(
                width=2,
                color='rgb(255, 204, 0)',
            ),
            showlegend = False,
            hoverinfo = 'none'
            )
    injury_data.append(trace_unlisted)
    
    layout = go.Layout(
        title='Injury Report for {}'.format(player.name),
        width=950,
        height=500,
        showlegend=False,
        dragmode='pan',
        margin=go.Margin(
            l=10,
            r=10,
            b=10,
            t=60,
            pad=0
        ), images= [dict(
            source= "https://raw.githubusercontent.com/p1ho/si-507-final-project-p1ho/master/3d_human.png",
            xref= "x",
            yref= "y",
            x= -.5,
            y= 2.6,
            sizex= 1,
            sizey= 2.6,
            sizing= "stretch",
            opacity= 1,
            layer= "below"
        )], xaxis=dict(
            autorange=False,
            showgrid=False,
            zeroline=False,
            showline=False,
            autotick=False,
            dtick = .1,
            showticklabels=False,
            range = [-2.5, 2.5]
        ), yaxis=dict(
            autorange=False,
            showgrid=False,
            zeroline=False,
            showline=False,
            autotick=False,
            dtick = .1,
            showticklabels=False,
            range = [-0, 2.6]
        )
    )
    fig=go.Figure(data=injury_data,layout=layout)
    py.plot(fig, validate=False, filename="{}-injury-report".format(player.name))
    print("Plot generated and opened in the web browser.")
    print("="*20)

# Short-hand for dictionary accumulation
def dict_accum_helper(dict, key, value):
    if key in dict:
        dict[key].append(value)
    else:
        dict[key] = [value]
    
# Handles User Interaction with the program
# Parameter: nothing
# Returns: nothing
def interaction():
    while True:
        input_ = input("Please Enter NBA player name for Injury Report (or exit to stop program): ")
        if input_.lower().strip() == "exit":
            print("Bye!")
            break
        while len(input_.split()) > 2:
            input_ = input("Invalid Player Name: Please enter just the First Name and Last Name: ")
        player = Player(get_player_data(input_))
        plot(player)
    
   
if __name__=="__main__":
    interaction()