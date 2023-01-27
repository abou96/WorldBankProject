# WorldBankProject


The test consists in recovering data on countries as provided by World Bank which is providing a REST API to obtain multiple information on countries (find the related information at https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures ).
Many indicators on countries can be obtained as listed at: https://data.worldbank.org/indicator?tab=all

Among the different exposure to risk that can exist between different third-party companies, a specific one called ESG (standing for Environmental, Social, and Governance) is of particular interest for companies. To evaluate those, an overall score based on multiple features can be established. As an example, for the environmental score, methane production is one of these.  For this test we will focus on the variable called Methane emissions (kt of CO2 equivalent). This value can be obtained for most of the countries and for an extended period of time. This technical test consists in creating a RestAPI with a specific endpoint that will be able to return the Methane emissions for a country at a specific year.

Project to handle:
Create a project on git containing your code that will:
Recover the Methane emissions values for all countries and for all years,
Give an estimate on the Methane emissions for countries where the information is missing and justify the approach used,
Compute the uncertainty on your estimation when the value is missing,
Obtain and estimate when possible the Methane emissions for the last 10 years in all countries,  
Give an estimate of the Methane emissions for all countries for the next 5 years
Provide a score related to the Methane emissions value in each country, justify the methodology used. The score should be an index going from 0 to 4, where 0 stands for a “good” environmental result and 10 for the ”worst” environmental result. 

When all these values will be obtained, create a RestAPI (preferably fastAPI) with an endpoint which could take as input:
the iso alpha 2 code for a country, (must be provided)
the year (should be defined in 2013-2028), (optional)
And will return (in a json format):
The Methane emissions value of the defined country at a specific year (float),
The knowledge if the value is measured or estimated (boolean),
The iso alpha 2 code of the country (string), 
The country name (string),
The uncertainty on the Methane emissions,
The score/index for this country
If you find any relevant information that could be added to the response, do not hesitate to add it.

Hint: to minimise the uncertainty on the imputed values, do not hesitate to consider other variables proposed by World Bank.

When done, mail us the path to your git repo so we can have a first look at it before the next meeting where you will present your project in more detail.
During our next meeting you will be asked to present the obtained results on three different countries (each one from a different continent) that you will have chosen.

If you have any question concerning the task, do not hesitate to come back to us,

Yours,