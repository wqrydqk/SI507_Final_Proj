1. The structure of the Git repository
   - data_access_code/ --------- the directory used for data checkpoint
   - proj_flask/ --------- the directory used for final project, a flask                    	                     app
       - database/
           airport_database.sqlite ---------- a database containing some    	                                       static data, same as the one                    	                                       shown in data checkpoint 	                   	                                      (Note: the same file is also 					             contained in                 					             data_access_code/ directory)
        - static/ ---------- the directory containing the pictures used in 		                 this app
        - template/ ----------- the directory containing the flask 	   		                    templates for this app
        .gitignore ----------- ignore the secrets.py and __pycache__
        app_main.py ---------- main file to run the app
        check data.py --------- check the # of element in each cache files
        city_location.json -------- cache file for city location
        city_location_attraction.json --------- cache file for attractions                  	                                          in a certain city
        hotels_cache.json ------- cache file for the hotels near a certain 					  attraction

2. API Keys
Three apis are used in this project, and they are all accessed by api keys
a. OpenTripMap Places REST API v0.1
Go to the url: https://opentripmap.io/product, and apply for the api key by email, it is free.

b. Local Weather REST API
Go to the url: https://developer.weatherunlocked.com/, and apply for the api key using school email, it is free. Then the api key and your app id will be available.

c. Yelp Fusion REST API
Go to the url: https://www.yelp.com/developers/, and sign up a develop account using school email there, the api-key will be provided for free.

3. Mapbox Token
Besides the api keys, when using plotly to plot the attractions on map, we used the Mapbox Map, which requires a token. One should go to the url: https://account.mapbox.com/, and sign in there to apply for the token. Only with this token can we plot out the map and the attraction points.

4. Required Packages:
a. For the main file to run the app:
flask, requests, plotly, pandas.

b. For the file to set up the database: (already included in data-checkpoint)
requests, bs4.

5. Instruction on running the app and interacting with it.
a. In proj_flask directory, run app_main.py directly, then the app is running.

b. Then user can get to http://127.0.0.1:5000/, and will see the index page. At the top of this page, user can input his/her interested city, select one type of attractions in this city, and indicate the presentation type; at the bottom of this page, user can input his/her departure city, destination city, and travel date to search for tickets. Then two forms are submitted separately.

c. By submitting the form on the top, the user can see the attractions and the weather in the city, he/she can then select one of the attractions to do a further search on the hotels near that attraction, and view the hotels there; by submitting the form at the bottom, the user will be directed to http://www.skyscanner.com to view the tickets.

d. The detailed interaction/presentation instruction will be covered in PART 4(in the submitted pdf) and the demo video at https://www.youtube.com/watch?v=Bso_EGK6IBc

