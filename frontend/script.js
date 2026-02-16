// standard stuff to get
const DropZone = document.getElementById('dropZone')
const FileInput = document.getElementById('fileInput')
const FileLabel = document.getElementById('fileLabel')
const SubmitBtn = document.getElementById('submitBtn')
const UploadSection = document.getElementById('uploadSection')
const ResultsSection = document.getElementById('resultsSection')
const LoadingOverlay = document.getElementById('loadingOverlay')
const ResultImagePreview = document.getElementById('resultImagePreview')
const ToggleTechStatsBtn = document.getElementById('toggleTechStatsBtn')
const TechStatsContainer = document.getElementById('techStatsContainer')
const ResetBtn = document.getElementById('resetBtn')
const MainResultText = document.getElementById('mainResultText')
const GeneralStatsGrid = document.getElementById('generalStatsGrid')
const TechStatsGrid = document.getElementById('techStatsGrid')
// getting the circle overlay so we can slap some divs on it
const CircleOverlay = document.getElementById('circleOverlay')


//yare yare dazes



// this is what keeps track of what the app is doing rn
let appState = "idle"
// this is where we will store the actual picture they upload
let currentThermalImage = null

// setting a fake delay of 2.5 seconds to make it look like our program is very power intensive
const FAKE_NETWORK_DELAY = 2500 

// this function takes the stats array and turns it into html blocks so we dont get collision tings innit brevski
const generateStatsHTML = (statsArray) => {


    // we map over every stat in the array and return a string of html
    return statsArray.map(stat => `

        <div class="stat-card">
            <div class="stat-label">${stat.label}</div>
            <div class="stat-value">${stat.value}</div>
        </div>
    
    `).join('')
    // then we join it together



}



// function to handle the files when they get dropped or clicked
const handleFiles = (files) => {

    // checking if they actually gave us a file and didnt just bait us out
    if (files.length > 0) {


        // gets the first file they gave us
        const file = files[0]
        
        // checking if the file is actually an image and not a virus or smth
        if (!file.type.startsWith('image/')) {
            // logging this to console so i know they messed up
            console.log("invalid!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            // telling the user they need to pick an image
            alert("please select a valid image file.")
            


            return
        }
        
        // saving the file to our global variable so we can send it to the backend later
        currentThermalImage = file

        // updating the text to show the name of the file they picked
        FileLabel.textContent = `Selected: ${file.name}`
        // turning on the submit button so they can click it now
        SubmitBtn.disabled = false

        // making a new file reader object to read the image data
        // used gpt coz i was so baffed but basically u have to create a new object
        // otherwise u have 2 pointers pointing to the same thing and yh a madness happens
        const reader = new FileReader()

        // telling the reader what to do when it finishes reading the file
        reader.onload = (e) => {
            // setting the source of our preview image to the data it just read
            ResultImagePreview.src = e.target.result
        }

        // actually telling the reader to start reading the file as a data url
        reader.readAsDataURL(file)
    }
}





// function to show the results when the backend sends them back
const displayResults = (data) => {


    // hiding the loading spinner because we are done thinking
    LoadingOverlay.style.display = 'none'
    // hiding the upload section so they cant upload another one yet
    UploadSection.classList.add('hidden')

    // changing the main text to whatever the backend said the summary is
    MainResultText.textContent = data.summary



    // shoving the html we generated into the general stats grid
    GeneralStatsGrid.innerHTML = generateStatsHTML(data.generalStats)
    // shoving the html we generated into the tech stats grid (same same... but differenttttttttttttttttttttt)
    TechStatsGrid.innerHTML = generateStatsHTML(data.technicalStats)

    // wiping any old circles just in case so we dont get collision tings innit brevski
    CircleOverlay.innerHTML = ''

    // checking if the backend sent us any cold bridge coordinates
    if (data.coldBridges && data.coldBridges.length > 0) {
        
        // looping over each cold bridge coordinate the backend sent
        data.coldBridges.forEach(bridge => {
            
            // creating a new div element to be our circle
            const circle = document.createElement('div')
            // adding the class so it gets the css styles and glow
            circle.className = 'cold-bridge-circle'
            
            // setting the x position (left) based on the percentage
            circle.style.left = `${bridge.x}%`
            // setting the y position (top) based on the percentage
            circle.style.top = `${bridge.y}%`
            // setting the width based on the radius
            circle.style.width = `${bridge.radius}px`
            // setting the height based on the radius
            circle.style.height = `${bridge.radius}px`
            
            // slapping the circle onto the overlay container so it shows up on the image
            CircleOverlay.appendChild(circle)
        })
    }

    // finally showing the whole results section to the user
    ResultsSection.style.display = 'block'
}




// looping over the dragenter and dragover events
;['dragenter', 'dragover'].forEach(eventName => {

    // adding an event listener to the drop zone for each of those events
    DropZone.addEventListener(eventName, (e) => {

        // stopping the browser from doing its default thing
        e.preventDefault()
        // stopping the event from bubbling up the dom
        e.stopPropagation()
        // adding the dragover class so it lights up and looks cool
        DropZone.classList.add('dragover')


    // passing false for the capture phase thingy
    }, false)
})

// looping over the dragleave and drop events (repeat of above basically)
;['dragleave', 'drop'].forEach(eventName => {


    DropZone.addEventListener(eventName, (e) => {

        e.preventDefault()
        e.stopPropagation()
        DropZone.classList.remove('dragover')
    }, false)
})

// adding an event listener for when they actually drop the file
DropZone.addEventListener('drop', (e) => {



    // grabbing the data transfer object from the event
    const dt = e.dataTransfer
    // getting the list of files from the data transfer object
    const files = dt.files

    // passing those files to our handleFiles function to do the heavy lifting
    handleFiles(files)
})

// adding an event listener for when they click the drop zone instead of dragging
DropZone.addEventListener('click', () => FileInput.click())

// adding an event listener to the invisible file input for when its value changes
FileInput.addEventListener('change', (e) => handleFiles(FileInput.files))

// adding an event listener to the toggle button for the stats
ToggleTechStatsBtn.addEventListener('click', () => {


    // toggling the active class on the container so it shows or hides
    TechStatsContainer.classList.toggle('active')
    // checking if it currently has the active class


    if (TechStatsContainer.classList.contains('active')) {
        // changing the button text to say hide if it's currently showing
        ToggleTechStatsBtn.textContent = "Hide Technical Stats ^"


    } else {
        // changing the button text to say show if it's currently hidden
        ToggleTechStatsBtn.textContent = "Show Technical Stats v"
    }
})

// adding an event listener to the reset button
ResetBtn.addEventListener('click', () => {


    // wiping the current image variable back to null
    currentThermalImage = null
    FileInput.value = ''
    FileLabel.textContent = ''



    SubmitBtn.disabled = true
    ResultImagePreview.src = ''

    // wiping the circle overlay back to nothing
    CircleOverlay.innerHTML = ''

    // hiding the tech stats container just in case it was open
    TechStatsContainer.classList.remove('active')
    // resetting the toggle button text back to default
    ToggleTechStatsBtn.textContent = "Show Technical Stats ⬇️"

    // hiding the results section
    ResultsSection.style.display = 'none'
    // showing the upload section again so they can start over
    UploadSection.classList.remove('hidden')
    // resetting our app state variable back to idle
    appState = "idle"
})



// adding an event listener to the submit button
SubmitBtn.addEventListener('click', () => {


    // checking if there is no image selected (for safetu innit buttckeeks)
    if (!currentThermalImage) {
        // screaming into the void of the console because this shouldn't happen
        console.log("erorrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr")
        // stopping the function because we can't analyze nothing
        return
    }

    // changing the app state to analyzing
    appState = "analyzing"
    // logging that we are starting and printing the file name
    console.log("analysis started! preparing to send file to backend:", currentThermalImage.name)

    // showing the loading overlay so the user knows to hold their horses
    LoadingOverlay.style.display = 'flex'


    // essentially the goal of this part is to predict, is the backend gonna send back a cold bridge
    // what i tried to do is create a delay that no api can skip which is like a timer around the request
    // and if it does then it rerolls the mock data until it doesnt


    // setting a timeout to fake a network request
    setTimeout(() => {
        // logging that the fake backend finally replied
        console.log("backend response received.")

        // creating a fake response object that looks like what the real backend will send
        const mockResponseBad = {
            // saying the request worked
            success: true,
            // saying yes we found a cold bridge
            detected: true,
            // giving a short summary of what we found
            summary: "Significant Thermal Bridging Detected",

            // creating an array of cold bridge coordinates using percentages so it scales properly
            // x and y are percentages of the image width/height, radius is in pixels
            coldBridges: [
                { x: 50, y: 30, radius: 100 },
                { x: 70, y: 75, radius: 45 }
            ],

            // creating an array of general stats to show
            generalStats: [

                { label: "Lowest Temp Found", value: "12.4°C" },
                { label: "Average Surface Temp", value: "18.2°C" },
                { label: "Affected Area", value: "~15%" }
            ],
            // creating an array of technical nerdy stats to show
            technicalStats: [
                { label: "Est. Psi Value (Ψ)", value: "0.45 W/mK" },
                { label: "Local U-Value Est.", value: "1.8 W/m²K" }
            ]
        }
        // ^^ ai wrote this mock data btw

        // passing our fake data into the display function so it shows up on screen
        // game reberu wa ageru
        // orewa egoista itoshi 
        displayResults(mockResponseBad)

    // passing our fake delay constant to the timeout function
    }, FAKE_NETWORK_DELAY)
})