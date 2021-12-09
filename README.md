Personalised Covid Dashboard

This dashboard has been created to allow the user to set their location and receive updates on covid data and news articles based on that location.
To use this, direct yourself to the config.json file attached. In there, you may assign your country and local area to the respective variables so the dashboard can tailor the covid 
data to your area. 
You will also need to input your own ApiKey for the newsApi which is used in this dashboard, which can be obtained via this website https://newsapi.org/register.
This will usually look like a long sequence of different characters. Do not share your API key, as this might lead to you losing access to the news API.
Enter your API key in quotation marks in the API key section.
Once these variables have been set, run the covid_news_handling.py file.
In the terminal you will be shown a link to the covid dashboard (The application will be run on a local server, and will be accessible in your browser at the address: http://127.0.0.1:5000/index.)
Once clicked you will be directed to the dashboard through your device's default internet browser.
Once opened, you will be shown the Personalised covid dashboard with your assigned area's covid data. Also there will be five news articles on the right which are the most popular
news articles related to the Covid-19 pandemic.
To schedule data updates for a given time, select a time in the drop-down box under 'Schedule data updates'.
Select an update time of your choosing, along with options to repeat this update at this time and whether you would like the covid data or news articles to update, or both.
Click submit and you will see your scheduled updates on the right hand side of the website.
Note that the dashboard will retain full functionality as long as it is being run. 
Exiting or interrupting the command line when the application is running will stop the execution. Any scheduled updates will be deleted.
