  <p align="center"><a href="http://williamandmary.net" target="_blank" rel="noopener noreferrer"><img src="static/favicon/android-chrome-192x192.png?raw=true" alt="re-frame logo"></a></p>

# Ampersand Courselist & Campus Assistant
*Ampersand Courselist* is a comprehensive tool designed to help William & Mary students easily search for courses, prepare for registration, and navigate the campus more efficiently. With this website, you can easily search for courses based on a variety of criteria, including subject, instructor, credit hours, and more. This vastly expands the functionality of the open courselist website, while also providing a more modern, responsive user interface. Additionally, *Ampersand Courselist* provides students with information about building locations and distances to better fine-tune their schedule while planning their term.

Beyond course search and details, *Ampersand Courselist* also provides students with valuable information about campus layout, as mentioned above. This includes all academic buildings and an in-depth navigation assistant for ISC (everyone's favorite maze). In the future this will expand to include administrative and resident buildings as well, along with per-building maps to best navigate every environment. With *Ampersand Courselist*, you can quickly and easily find all the information you need so that you can make the most of your time at William & Mary!

## Inspiration
William & Mary can be an overwhelming school when you first arrive, with so many classes to choose, buildings laid out in confusing ways, and a campus that zigs and zags all over the place. With this set of tools, students will have a much easier time learning about course offerings, building their schedule, and then making sure they can actually get around to classes!

## Functionality
*Ampersand Courselist* has three primary functionalities:
1. The first and foremost is being a courselist for students to use. This has more filtering options, an updated UI, and can accept more complicated queries so students can search for exactly what they want.
2. A map of campus that can display the distances between buildings using Google Maps API to get walking distance and time, and eventually provide information about each building such as the departments it contains or the purpose of each building. This combines with an easily readable graphic showing the building to be a helpful utility for new students especially.
3. An assistant for navigating ISC, based on pathfinding between specific rooms. This is built on a very flexible node-based structure that will be expanded to include instructions in English on where to go, turning the indicators into a full guide of the building. Floor 1 of ISC is completed as a demo of the concept.

## Project Structure
*Ampersand Courselist* is built using a Flask backend that is hosted through Google Cloud with Firebase. The courselist application uses scheduled functions to interface with the W&M Open Courselist API to pull data for each term, each subject, and every single class, compiling it into a Realtime Firebase NoSQL Database. This database is the real core of the course functionality. The other data on buildings is scraped using Selenium and then it's all put together into one great website with a lot of imagery and CSS.

## What's next for *Ampersand Courselist*
#### ISC Assistant
1. Expand ISC Assistant to all floors of ISC and allow for routing between floors
2. Subsequently, allowing clicking on specific rooms to navigate from there or take the room as input from classes taking place in ISC
3. Embed instructions into each ISC path as to how to walk around so that when the paths are read back they can form a guide

#### *Ampersand Courselist*
1. Rework the mobile UI of the database results to be even more responsive and show course data more helpfully
2. Get specific details for every course to allow filtering by building, time, and more
3. Continue to add features requested by our peers

#### Campus Routing
1. Display walking route between buildings
2. Scrape for data on every type of building and landmark on campus, not just academic
3. Expand to the School of Ed and Law School
4. Add data for each building on the purpose and a link to the building's webpage
5. Make a more interactable map that can display all these building attributes

Thanks for checking out our project!
