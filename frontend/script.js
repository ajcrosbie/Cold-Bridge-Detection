// standard stuff to get
const DropZone = document.getElementById('dropZone')
const FileInput = document.getElementById('fileInput')
const FileLabel = document.getElementById('fileLabel')
const FileError = document.getElementById('fileError')
const SubmitBtn = document.getElementById('submitBtn')
const UploadSection = document.getElementById('uploadSection')
const ResultsSection = document.getElementById('resultsSection')
const LoadingOverlay = document.getElementById('loadingOverlay')
const LoadingText = document.getElementById('loadingText')
const ResetBtn = document.getElementById('resetBtn')
const MainResultText = document.getElementById('mainResultText')
const GeneralStatsGrid = document.getElementById('generalStatsGrid')
const TechStatsGrid = document.getElementById('techStatsGrid')
const SelectedFilesSection = document.getElementById('selectedFilesSection')
const SelectedFilesList = document.getElementById('selectedFilesList')
const AnalysedImagesList = document.getElementById('analysedImagesList')
const GraphTitle = document.getElementById('graphTitle')
const GraphSubtitle = document.getElementById('graphSubtitle')
const GraphPlaceholder = document.getElementById('graphPlaceholder')
const GraphWrapper = document.getElementById('graphWrapper')
const ApiGraphCanvas = document.getElementById('apiGraphCanvas')
const AdvancedResultsSection = document.getElementById('advancedResultsSection')
const ShowAdvancedInfoCheckbox = document.getElementById('showAdvancedInfoCheckbox')
const InternalTempInput = document.getElementById('internalTempInput')
const ExternalTempInput = document.getElementById('externalTempInput')
const WallWidthInput = document.getElementById('wallWidthInput')
const WallHeightInput = document.getElementById('wallHeightInput')
const InternalTempError = document.getElementById('internalTempError')
const ExternalTempError = document.getElementById('externalTempError')
const WallWidthError = document.getElementById('wallWidthError')
const WallHeightError = document.getElementById('wallHeightError')


//yare yare dazes



// this is what keeps track of what the app is doing rn
let appState = 'idle'
// this is where we will store the actual pictures they upload
let currentThermalImages = []
// this is for the graph once the api sends us some numbers back
let apiGraphInstance = null

// setting a fake delay of 2 seconds to make it feel like the backend is doing some real work
const FAKE_NETWORK_DELAY = 2000
// this is the list of file types we are happy with
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/tiff', 'image/tif']
// this is the list of file extensions we are happy with
const ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.tif', '.tiff']



// this function takes the stats array and turns it into html blocks so we dont get collision tings innit brevski
const generateStatsHTML = (statsArray) => {


    // if the array is empty we just return nothing
    if (!statsArray || statsArray.length === 0) {
        return ''
    }

    // we map over every stat in the array and return a string of html
    return statsArray.map(stat => `

        <div class="stat-card">
            <div class="stat-label">${stat.label}</div>
            <div class="stat-value">${stat.value}</div>
        </div>
    
    `).join('')
    // then we join it together



}



// this checks if the file extension looks valid
const hasValidImageExtension = (fileName) => {


    // converting the name to lowercase so the check works properly
    const lowerName = fileName.toLowerCase()

    // checking if it ends with any valid extension
    return ALLOWED_IMAGE_EXTENSIONS.some(extension => lowerName.endsWith(extension))
}



// this checks if a file is a zip
const isZipFile = (file) => {


    // checking both the mime type and the file extension because browsers like to move weird sometimes
    return file.type === 'application/zip' || file.name.toLowerCase().endsWith('.zip')
}



// this checks if a file is an image we want to allow
const isAllowedImageFile = (file) => {


    // checking the mime type first
    if (ALLOWED_IMAGE_TYPES.includes(file.type)) {
        return true
    }

    // if mime type is missing or weird we fall back to the file name
    return hasValidImageExtension(file.name)
}



// this guesses the mime type for files we pull out of the zip
const getMimeTypeFromName = (fileName) => {


    // converting to lowercase so the check is consistent
    const lowerName = fileName.toLowerCase()

    // returning the mime type based on the extension
    if (lowerName.endsWith('.jpg') || lowerName.endsWith('.jpeg')) return 'image/jpeg'
    if (lowerName.endsWith('.png')) return 'image/png'
    if (lowerName.endsWith('.tif') || lowerName.endsWith('.tiff')) return 'image/tiff'

    // if it somehow doesnt match, send back empty string
    return ''
}



// this makes a unique enough id for each image card
const makeImageId = () => {


    // combining time + random string so our image cards dont clash
    return `img-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}



// this wipes all the red validation states
const clearValidationErrors = () => {


    // clearing the upload file error
    FileError.textContent = ''
    DropZone.classList.remove('field-invalid')

    // clearing the normal form field errors
    ;[
        { input: InternalTempInput, error: InternalTempError },
        { input: ExternalTempInput, error: ExternalTempError },
        { input: WallWidthInput, error: WallWidthError },
        { input: WallHeightInput, error: WallHeightError }
    ].forEach(field => {
        field.input.classList.remove('input-invalid')
        field.error.textContent = ''
    })

    // clearing every image card error as well
    currentThermalImages.forEach(image => {
        image.hasNameError = false
    })
}



// this marks a normal input as invalid and writes the error under it
const showInputError = (inputElement, errorElement, message) => {


    // adding the red border
    inputElement.classList.add('input-invalid')
    // writing the message
    errorElement.textContent = message
}



// this marks the upload area as invalid and writes the error under it
const showFileError = (message) => {


    // putting a red border around the whole drop area
    DropZone.classList.add('field-invalid')
    // writing the message under it
    FileError.textContent = message
}



// this updates the submit button and file label based on what they have selected
const updateSelectionSummary = () => {


    // if there are no images selected we reset everything
    if (currentThermalImages.length === 0) {
        FileLabel.textContent = ''
        SubmitBtn.disabled = true
        SelectedFilesSection.classList.add('hidden')
        return
    }

    // otherwise we show how many images are currently in the stack
    FileLabel.textContent = `${currentThermalImages.length} image${currentThermalImages.length === 1 ? '' : 's'} ready`
    SubmitBtn.disabled = false
    SelectedFilesSection.classList.remove('hidden')
}



// this builds the html card list for every selected image
const renderSelectedFiles = () => {


    // if there is nothing selected then just hide the section
    if (currentThermalImages.length === 0) {
        SelectedFilesList.innerHTML = ''
        updateSelectionSummary()
        return
    }

    // wiping the current cards so we can redraw them
    SelectedFilesList.innerHTML = ''

    // looping through every image object we currently have stored
    currentThermalImages.forEach(image => {

        // making the card wrapper
        const card = document.createElement('div')
        card.className = 'selected-file-card'

        // putting the html into the card
        card.innerHTML = `
            <div class="selected-file-preview-wrap">
                <img src="${image.previewUrl}" alt="${image.file.name}" class="selected-file-preview">
            </div>
            <div class="selected-file-meta">
                <div class="selected-file-name">${image.file.name}</div>
                <div class="selected-file-source">${image.sourceLabel}</div>
            </div>
            <div class="selected-file-input-wrap">
                <label for="name-${image.id}">Image name / location</label>
                <input type="text" id="name-${image.id}" class="selected-file-input ${image.hasNameError ? 'input-invalid' : ''}" placeholder="e.g. Front bedroom left wall" value="${image.locationName}"> 
                <div class="field-error">${image.hasNameError ? 'You must name this image before submitting.' : ''}</div>
            </div>
            <button class="remove-file-btn" data-image-id="${image.id}" type="button">Remove</button>
        `

        // grabbing the input so we can keep the name synced to state
        const nameInput = card.querySelector('.selected-file-input')
        // grabbing the remove button so they can bin a bad image
        const removeBtn = card.querySelector('.remove-file-btn')

        // listening for changes to the name/location input
        nameInput.addEventListener('input', (e) => {

            // saving whatever they typed into the image object
            image.locationName = e.target.value

            // if they have typed something then we can clear the name error without nuking focus
            if (image.locationName.trim()) {
                image.hasNameError = false
                nameInput.classList.remove('input-invalid')
                const localError = card.querySelector('.field-error')
                localError.textContent = ''
            }
        })

        // listening for the remove button
        removeBtn.addEventListener('click', () => {

            // removing the image from the array
            removeImageById(image.id)
        })

        // finally slapping the card onto the page
        SelectedFilesList.appendChild(card)
    })

    // updating the summary once the cards are done
    updateSelectionSummary()
}



// this removes an image and cleans up its preview url
const removeImageById = (imageId) => {


    // finding the image we are about to remove
    const imageToRemove = currentThermalImages.find(image => image.id === imageId)

    // cleaning up the object url so we dont leak memory like a hooligan
    if (imageToRemove) {
        URL.revokeObjectURL(imageToRemove.previewUrl)
    }

    // filtering it out from the main list
    currentThermalImages = currentThermalImages.filter(image => image.id !== imageId)

    // redrawing the ui
    renderSelectedFiles()
}



// this turns a file into the object shape our app wants
const buildImageObject = (file, sourceLabel = 'Uploaded directly', locationName = '') => {


    // returning our standard shape for each image
    return {
        id: makeImageId(),
        file,
        previewUrl: URL.createObjectURL(file),
        locationName: locationName, // pre-fills if they give folder name
        hasNameError: false,
        sourceLabel
    }
}



// this digs through a zip and pulls out only valid images
const extractImagesFromZip = async (zipFile) => {


    // opening the zip file using jszip
    const zip = await JSZip.loadAsync(zipFile)
    // this array will hold every image we manage to get out
    const extractedImages = []

    // getting all the file paths inside the zip
    const zipEntries = Object.values(zip.files)

    // looping through every entry one by one
    for (const entry of zipEntries) {

        // skipping folders because obviously we cant analyse a folder
        if (entry.dir) {
            continue
        }

        // checking if the file name in the zip looks like an allowed image
        if (!hasValidImageExtension(entry.name)) {
            continue
        }

        // getting the blob from the zip entry
        const blob = await entry.async('blob')
        // guessing the mime type from the original file name
        const mimeType = getMimeTypeFromName(entry.name)
        // keeping only the actual file name without all the zip folder guff
        const cleanName = entry.name.split('/').pop()

        // split the path and get the parent folder's name if it exists
        const pathParts = entry.name.split('/')
        // if it's inside a folder, get the folder name, if loose in the zip, call it "Unlabelled"
        const folderName = pathParts.length > 1 ? pathParts[pathParts.length - 2] : ''

        // making a real file object out of the blob so the rest of the app can use it normally
        const extractedFile = new File([blob], cleanName, { type: mimeType || blob.type || 'application/octet-stream' })

        // pushing the processed image into our output array
        extractedImages.push(buildImageObject(extractedFile, `Extracted from ${zipFile.name}`, folderName))
    }

    // sending back whatever images we found
    return extractedImages
}



// this takes the dropped files / chosen files and filters them properly
const handleFiles = async (files) => {


    // clearing previous upload errors first
    FileError.textContent = ''
    DropZone.classList.remove('field-invalid')

    // checking if they actually gave us something
    if (!files || files.length === 0) {
        return
    }

    // showing a quick loading message while we process zip files and previews
    LoadingText.textContent = 'Preparing files...'
    LoadingOverlay.style.display = 'flex'

    // making arrays to keep track of what was valid and what was not
    const newImages = []
    const invalidFiles = []

    try {

        // looping over every file they dropped/selected
        for (const file of Array.from(files)) {

            // if it is a zip file then we extract it
            if (isZipFile(file)) {
                const zippedImages = await extractImagesFromZip(file)

                // if the zip had no usable images we mark it as invalid
                if (zippedImages.length === 0) {
                    invalidFiles.push(`${file.name} (no supported images found inside the ZIP)`)
                    continue
                }

                // otherwise we slap all the extracted images into the new images array
                newImages.push(...zippedImages)
                continue
            }

            // if it is just a normal image file then we accept it
            if (isAllowedImageFile(file)) {
                newImages.push(buildImageObject(file))
                continue
            }

            // if it reaches here then it is not something we accept
            invalidFiles.push(file.name)
            
        }

        // deduping by name + size + lastModified so we dont stack accidental doubles forever
        newImages.forEach(newImage => {
            const alreadyExists = currentThermalImages.some(existingImage => {
                return existingImage.file.name === newImage.file.name &&
                    existingImage.file.size === newImage.file.size &&
                    existingImage.file.lastModified === newImage.file.lastModified
            })

            if (!alreadyExists) {
                currentThermalImages.push(newImage)
            } else {
                URL.revokeObjectURL(newImage.previewUrl)
            }
        })

        // redrawing the selected file cards
        renderSelectedFiles()

        // if anything was invalid we show that in red without nuking the valid files
        if (invalidFiles.length > 0) {
            showFileError(`Only ZIP files containing those image types are allowed. Problem files: ${invalidFiles.join(', ')}`)
        }

    } catch (error) {

        // if zip extraction or something else explodes then we show a clean error
        console.error('file processing failed:', error)
        showFileError('That ZIP or file could not be processed. Please upload valid thermal images only.')
    }

    // clearing the real file input so the same file can be picked again later if needed
    FileInput.value = ''

    // hiding the loading overlay once file processing is done
    LoadingOverlay.style.display = 'none'
    LoadingText.textContent = 'Analysing...'
}



// this checks that every required thing is actually filled in before we submit
const validateForm = () => {


    // clearing all old errors first
    clearValidationErrors()

    // assuming everything is valid until proven otherwise
    let isValid = true

    // checking we actually have some images to analyse
    if (currentThermalImages.length === 0) {
        showFileError('You must upload at least one thermal image or ZIP file before submitting.')
        isValid = false
    }

    // checking internal temp
    if (InternalTempInput.value.trim() === '') {
        showInputError(InternalTempInput, InternalTempError, 'You must enter the internal temperature.')
        isValid = false
    }

    // checking external temp
    if (ExternalTempInput.value.trim() === '') {
        showInputError(ExternalTempInput, ExternalTempError, 'You must enter the external temperature.')
        isValid = false
    }

    // checking wall width
    if (WallWidthInput.value.trim() === '') {
        showInputError(WallWidthInput, WallWidthError, 'You must enter the wall width.')
        isValid = false
    }

    // checking wall height
    if (WallHeightInput.value.trim() === '') {
        showInputError(WallHeightInput, WallHeightError, 'You must enter the wall height.')
        isValid = false
    }

    // checking internal temp is actually a number
    if (InternalTempInput.value.trim() !== '' && Number.isNaN(Number(InternalTempInput.value))) {
        showInputError(InternalTempInput, InternalTempError, 'Internal temperature must be a number.')
        isValid = false
    }

    // checking external temp is actually a number
    if (ExternalTempInput.value.trim() !== '' && Number.isNaN(Number(ExternalTempInput.value))) {
        showInputError(ExternalTempInput, ExternalTempError, 'External temperature must be a number.')
        isValid = false
    }

    // checking wall width is actually a number above 0
    if (WallWidthInput.value.trim() !== '' && (Number.isNaN(Number(WallWidthInput.value)) || Number(WallWidthInput.value) <= 0)) {
        showInputError(WallWidthInput, WallWidthError, 'Wall width must be a number greater than 0.')
        isValid = false
    }

    // checking wall height is actually a number above 0
    if (WallHeightInput.value.trim() !== '' && (Number.isNaN(Number(WallHeightInput.value)) || Number(WallHeightInput.value) <= 0)) {
        showInputError(WallHeightInput, WallHeightError, 'Wall height must be a number greater than 0.')
        isValid = false
    }

    // making sure every image has a name/location attached to it
    currentThermalImages.forEach(image => {
        if (!image.locationName.trim()) {
            image.hasNameError = true
            isValid = false
        }
    })

    // redrawing the cards so any missing image names go red
    renderSelectedFiles()

    // sending back whether the form passed or failed
    return isValid
}



// this takes whatever graph payload the api sends and normalises it
const normaliseGraphPayload = (graphData) => {


    // if there is no graph data then we just return null
    if (!graphData) {
        return null
    }

    // grabbing the title if it exists
    const title = graphData.title || 'Graph output'
    // grabbing the optional subtitle if it exists
    const subtitle = graphData.subtitle || 'This area is plotting the graph data returned by the API.'

    // if the api sends labels and values arrays already then we use those
    if (Array.isArray(graphData.labels) && Array.isArray(graphData.values) && graphData.labels.length === graphData.values.length) {
        return {
            title,
            subtitle,
            labels: graphData.labels,
            values: graphData.values
        }
    }

    // if the api sends dataPoints instead then we build labels and values from that
    if (Array.isArray(graphData.dataPoints) && graphData.dataPoints.length > 0) {
        const labels = []
        const values = []

        graphData.dataPoints.forEach((point, index) => {

            // if the point is just a number then we make a generic label for it
            if (typeof point === 'number') {
                labels.push(`Point ${index + 1}`)
                values.push(point)
                return
            }

            // if it is an object then we try to support common naming styles
            if (typeof point === 'object' && point !== null) {
                labels.push(point.label || point.x || `Point ${index + 1}`)
                values.push(point.value ?? point.y ?? 0)
            }
        })

        // if we managed to build a valid set then we return it
        if (labels.length > 0 && labels.length === values.length) {
            return {
                title,
                subtitle,
                labels,
                values
            }
        }
    }

    // if the payload shape is not usable yet we return null so the placeholder stays on screen
    return null
}



// this renders the graph area either as a placeholder or a real chart
const renderApiGraph = (graphData) => {


    // cleaning up any old chart instance first
    if (apiGraphInstance) {
        apiGraphInstance.destroy()
        apiGraphInstance = null
    }

    // normalising the payload into one clean structure
    const normalisedGraph = normaliseGraphPayload(graphData)

    // if we dont have usable graph data yet we keep the placeholder visible
    if (!normalisedGraph) {
        GraphTitle.textContent = 'Graph output'
        GraphSubtitle.textContent = 'This area will plot whatever title and data points the API sends back.'
        GraphPlaceholder.textContent = 'Waiting for API graph data.'
        GraphPlaceholder.classList.remove('hidden')
        GraphWrapper.classList.add('hidden')
        return
    }

    // updating the heading and subtitle from the api payload
    GraphTitle.textContent = normalisedGraph.title
    GraphSubtitle.textContent = normalisedGraph.subtitle

    // hiding the placeholder and showing the canvas
    GraphPlaceholder.classList.add('hidden')
    GraphWrapper.classList.remove('hidden')

    // creating the chart using the labels and values from the backend response
    apiGraphInstance = new Chart(ApiGraphCanvas, {
        type: 'line',
        data: {
            labels: normalisedGraph.labels,
            datasets: [
                {
                    label: normalisedGraph.title,
                    data: normalisedGraph.values,
                    borderWidth: 2,
                    tension: 0.2,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#eaeaea'
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#eaeaea'
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.08)'
                    }
                },
                y: {
                    ticks: {
                        color: '#eaeaea'
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.08)'
                    }
                }
            }
        }
    })
}



// this makes the image result cards for each analysed image
const renderAnalysedImages = (images) => {


    // wiping any old image cards
    AnalysedImagesList.innerHTML = ''

    // looping over every analysed image the backend sent back
    images.forEach(image => {

        // making the main result card
        const card = document.createElement('div')
        card.className = 'analysed-image-card'

        // putting the structure into the card
        card.innerHTML = `
            <div class="analysed-image-header">
                <div>
                    <h4>${image.locationName}</h4>
                    <p>${image.summary}</p>
                </div>
            </div>

            <div class="analysed-image-preview-container">
                <div class="analysed-image-wrapper">
                    <img src="${image.previewUrl}" alt="${image.locationName}" class="analysed-image-preview">
                    <div class="circle-overlay"></div>
                </div>
            </div>

            <div class="stats-grid image-stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Lowest Temp Found</div>
                    <div class="stat-value">${image.lowestTemp}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Average Surface Temp</div>
                    <div class="stat-value">${image.averageSurfaceTemp}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Affected Area</div>
                    <div class="stat-value">${image.affectedArea}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Error Margin</div>
                    <div class="stat-value">${image.errorMargin}</div>
                </div>
            </div>
        `

        // grabbing the overlay container
        const overlay = card.querySelector('.circle-overlay')

        // drawing all the cold bridge circles for this image
        image.coldBridges.forEach(bridge => {
            const circle = document.createElement('div')
            circle.className = 'cold-bridge-circle'
            circle.style.left = `${bridge.x}%`
            circle.style.top = `${bridge.y}%`
            circle.style.width = `${bridge.radius}px`
            circle.style.height = `${bridge.radius}px`
            overlay.appendChild(circle)
        })

        // slapping the finished card onto the page
        AnalysedImagesList.appendChild(card)
    })
}



// this makes some pretend backend results from the current files + form data
const createMockAnalysisResponse = () => {


    // grabbing the wall measurements and temperatures from the form
    const internalTemp = Number(InternalTempInput.value)
    const externalTemp = Number(ExternalTempInput.value)
    const wallWidth = Number(WallWidthInput.value)
    const wallHeight = Number(WallHeightInput.value)
    const wallArea = wallWidth * wallHeight
    const deltaT = Math.abs(internalTemp - externalTemp)

    // this array will hold all the per-image results
    const analysedImages = []

    // looping through every uploaded image and giving it a pretend result
    currentThermalImages.forEach((image, index) => {

        // making a slightly different severity for each image so the graph looks alive
        const severityIndex = Number((2.8 + (index * 0.9) + (deltaT * 0.12)).toFixed(1))
        // making a pretend lowest temp based on the delta temp and severity
        const lowestTemp = Number((internalTemp - (deltaT * 0.35) - (index * 0.7) - 1.8).toFixed(1))
        // making a pretend average surface temp
        const averageSurfaceTemp = Number((internalTemp - (deltaT * 0.18) - (index * 0.3)).toFixed(1))
        // making a pretend affected area percentage
        const affectedAreaPercent = Number((8 + (index * 3.4) + Math.min(deltaT * 0.45, 9)).toFixed(1))
        // making a pretend error margin
        const errorMargin = Number((0.4 + (index * 0.08)).toFixed(2))
        // making a pretend psi value
        const psiValue = Number((0.22 + (severityIndex * 0.04)).toFixed(2))
        // making a pretend u value
        const uValue = Number((1.1 + (severityIndex * 0.08)).toFixed(2))
        // making a pretend confidence score
        const confidence = Number((82 + (index * 3)).toFixed(0))

        // pushing the pretend analysed result into the array
        analysedImages.push({
            id: image.id,
            locationName: image.locationName,
            previewUrl: image.previewUrl,
            summary: severityIndex >= 5.5 ? 'Significant thermal bridging detected' : 'Moderate thermal bridging detected',
            severityIndex,
            lowestTemp: `${lowestTemp.toFixed(1)}°C`,
            averageSurfaceTemp: `${averageSurfaceTemp.toFixed(1)}°C`,
            affectedArea: `${affectedAreaPercent.toFixed(1)}%`,
            errorMargin: `±${errorMargin.toFixed(2)}°C`,
            psiValue: `${psiValue.toFixed(2)} W/mK`,
            uValue: `${uValue.toFixed(2)} W/m²K`,
            confidence: `${confidence}%`,
            coldBridges: [
                { x: 35 + (index * 8), y: 32 + (index * 6), radius: 90 - (index * 8) },
                { x: 68 - (index * 5), y: 70 - (index * 4), radius: 46 + (index * 3) }
            ]
        })
    })

    // working out a few global result numbers from all the images
    const lowestTempFound = Math.min(...analysedImages.map(image => Number(image.lowestTemp.replace('°C', ''))))
    const averageSurfaceTempOverall = analysedImages.reduce((sum, image) => sum + Number(image.averageSurfaceTemp.replace('°C', '')), 0) / analysedImages.length
    const averageAffectedArea = analysedImages.reduce((sum, image) => sum + Number(image.affectedArea.replace('%', '')), 0) / analysedImages.length
    const averageSeverity = analysedImages.reduce((sum, image) => sum + image.severityIndex, 0) / analysedImages.length
    const averagePsi = analysedImages.reduce((sum, image) => sum + Number(image.psiValue.replace(' W/mK', '')), 0) / analysedImages.length
    const averageU = analysedImages.reduce((sum, image) => sum + Number(image.uValue.replace(' W/m²K', '')), 0) / analysedImages.length
    const averageErrorMargin = analysedImages.reduce((sum, image) => sum + Number(image.errorMargin.replace('±', '').replace('°C', '')), 0) / analysedImages.length
    const affectedWallArea = wallArea * (averageAffectedArea / 100)

    // building the overall response object the rest of the ui expects
    return {
        success: true,
        summary: averageSeverity >= 5.5 ? 'Cold bridge risk detected across the uploaded set' : 'Moderate cold bridge risk detected across the uploaded set',
        generalStats: [
            { label: 'Images Analysed', value: `${analysedImages.length}` },
            { label: 'Lowest Temp Found', value: `${lowestTempFound.toFixed(1)}°C` },
            { label: 'Average Surface Temp', value: `${averageSurfaceTempOverall.toFixed(1)}°C` },
            { label: 'Affected Wall Area', value: `${affectedWallArea.toFixed(2)} m²` },
            { label: 'Wall Size Entered', value: `${wallArea.toFixed(2)} m²` },
            { label: 'Internal vs External ΔT', value: `${deltaT.toFixed(1)}°C` }
        ],
        technicalStats: [
            { label: 'Average Severity Index', value: averageSeverity.toFixed(1) },
            { label: 'Average Error Margin', value: `±${averageErrorMargin.toFixed(2)}°C` },
            { label: 'Est. Psi Value (Ψ)', value: `${averagePsi.toFixed(2)} W/mK` },
            { label: 'Local U-Value Est.', value: `${averageU.toFixed(2)} W/m²K` },
            { label: 'Confidence Range', value: `${analysedImages[0].confidence} to ${analysedImages[analysedImages.length - 1].confidence}` },
            { label: 'Expert Note', value: 'Use measured dimensions and calibrated thermal data for final reporting.' }
        ],
        // leaving graphData empty on purpose for now because the real api will decide the title and data points later
        graphData: null,
        analysedImages
    }
}



// this is where we would actually send the data to the backend later
const sendImagesForAnalysis = () => {


    // returning a promise so the submit flow looks like a real api call
    return new Promise((resolve) => {

        // waiting a little bit so the loading overlay actually appears
        setTimeout(() => {
            resolve(createMockAnalysisResponse())
        }, FAKE_NETWORK_DELAY)
    })
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

    // checking if the user wanted the advanced info at the top
    if (ShowAdvancedInfoCheckbox.checked && data.technicalStats && data.technicalStats.length > 0) {
        AdvancedResultsSection.classList.remove('hidden')
        TechStatsGrid.innerHTML = generateStatsHTML(data.technicalStats)
    } else {
        AdvancedResultsSection.classList.add('hidden')
        TechStatsGrid.innerHTML = ''
    }

    // drawing the graph from the backend response or showing the placeholder
    renderApiGraph(data.graphData)

    // drawing the image cards from the backend response
    renderAnalysedImages(data.analysedImages)

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
FileInput.addEventListener('change', () => handleFiles(FileInput.files))

// clearing errors live when the main inputs change
InternalTempInput.addEventListener('input', () => {
    InternalTempInput.classList.remove('input-invalid')
    InternalTempError.textContent = ''
})

ExternalTempInput.addEventListener('input', () => {
    ExternalTempInput.classList.remove('input-invalid')
    ExternalTempError.textContent = ''
})

WallWidthInput.addEventListener('input', () => {
    WallWidthInput.classList.remove('input-invalid')
    WallWidthError.textContent = ''
})

WallHeightInput.addEventListener('input', () => {
    WallHeightInput.classList.remove('input-invalid')
    WallHeightError.textContent = ''
})

// adding an event listener to the reset button
ResetBtn.addEventListener('click', () => {


    // cleaning up all the object urls before wiping state
    currentThermalImages.forEach(image => {
        URL.revokeObjectURL(image.previewUrl)
    })

    // wiping the current image array back to nothing
    currentThermalImages = []
    FileInput.value = ''
    FileLabel.textContent = ''
    FileError.textContent = ''

    // resetting the normal inputs
    InternalTempInput.value = ''
    ExternalTempInput.value = ''
    WallWidthInput.value = ''
    WallHeightInput.value = ''

    // resetting the advanced checkbox
    ShowAdvancedInfoCheckbox.checked = false

    // clearing any red borders from the form
    clearValidationErrors()

    // turning the button off until they upload some more stuff
    SubmitBtn.disabled = true

    // wiping the selected file cards
    SelectedFilesList.innerHTML = ''
    SelectedFilesSection.classList.add('hidden')

    // wiping the analysed image cards
    AnalysedImagesList.innerHTML = ''

    // destroying the graph if it exists
    if (apiGraphInstance) {
        apiGraphInstance.destroy()
        apiGraphInstance = null
    }

    // resetting the graph section back to the placeholder
    GraphTitle.textContent = 'Graph output'
    GraphSubtitle.textContent = 'This area will plot whatever title and data points the API sends back.'
    GraphPlaceholder.textContent = 'Waiting for API graph data.'
    GraphPlaceholder.classList.remove('hidden')
    GraphWrapper.classList.add('hidden')

    // hiding the advanced results section
    AdvancedResultsSection.classList.add('hidden')
    TechStatsGrid.innerHTML = ''

    // hiding the results section
    ResultsSection.style.display = 'none'
    // showing the upload section again so they can start over
    UploadSection.classList.remove('hidden')
    // resetting our app state variable back to idle
    appState = 'idle'
})



// adding an event listener to the submit button
SubmitBtn.addEventListener('click', async () => {


    // checking the whole form before we do anything
    if (!validateForm()) {
        console.log('validation failed so we are not submitting')
        return
    }

    // changing the app state to analyzing
    appState = 'analyzing'
    // logging that we are starting and printing the file count
    console.log('analysis started! preparing to send files to backend:', currentThermalImages.length)

    // showing the loading overlay so the user knows to hold their horses
    LoadingText.textContent = 'Analysing...'
    LoadingOverlay.style.display = 'flex'

    try {

        // waiting for the pretend backend to reply
        const response = await sendImagesForAnalysis()

        // passing our fake data into the display function so it shows up on screen
        displayResults(response)

    } catch (error) {

        // logging the error for debugging
        console.error('analysis failed:', error)
        // hiding the loading overlay if something broke
        LoadingOverlay.style.display = 'none'
        // showing a non-popup error near the upload zone
        showFileError('The analysis failed. Please check your files and try again.')
        // resetting state back to idle
        appState = 'idle'
    }
})