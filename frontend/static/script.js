// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    
    // Upload
    const imageInput = document.getElementById('imageInput');
    const uploadButton = document.getElementById('uploadButton')
    const imageContainer = document.getElementById('imageContainer');
    const spanWidth = document.getElementById('spanWidth')
    const spanHeight = document.getElementById('spanHeight')
    let uploadedImage = null;

    // Draw Box
    const boxInput = document.getElementById('boxInput');
    const drawBox = document.getElementById('drawBox')   
    let boxCoordinates = null;

    // Draw Points
    const addInput = document.getElementById('addInput');
    const drawPoints = document.getElementById('drawPoints');
    const inputContainer = document.getElementById('inputContainer');
    const form = document.getElementById('textInputForm')
    let points = null;

    // Predict Everything
    const predictButton = document.getElementById('predictEverything')

    // Upload
    uploadButton.addEventListener('click', () => {
        if (imageInput.files.length > 0) {
            const file = imageInput.files[0];
            const formData = new FormData();
            formData.append('image', file);

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                uploadedImage = data.image_path;
                width = data.width
                height = data.height

                // Update image width and height
                spanWidth.textContent = width
                spanHeight.textContent = height

                // Clear the image container before appending the new image
                imageContainer.innerHTML = '';
    
                // Append the new image to the container
                const imgElement = document.createElement('img');
                imgElement.src = uploadedImage + '?' + new Date().getTime();
                imgElement.alt = 'Uploaded Image';
                imageContainer.appendChild(imgElement);
            })
            .catch(error => console.error('Error uploading image:', error));
        }
    });

    // Draw Box
    drawBox.addEventListener('click', () => {
        const values = boxInput.value.split(',').map(Number);
        if (values.length === 4) {
            boxCoordinates = values;
        }

        if (boxCoordinates) {
            fetch('/drawBox', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ box_coordinates: boxCoordinates })
            })
            .then(response => response.json())
            .then(data => {
                uploadedImage = data.image_path;

                // Clear the image container before appending the new image
                imageContainer.innerHTML = '';
    
                // Append the new image to the container
                const imgElement = document.createElement('img');
                imgElement.src = uploadedImage + '?' + new Date().getTime();
                imgElement.alt = 'Uploaded Image';
                imageContainer.appendChild(imgElement);
            })                
            .catch(error => console.error('Error predicting:', error));
        }
    });

    // Draw Points
    drawPoints.addEventListener('click', () => {
        const dynamicInputs = form.querySelectorAll('.dynamic-input');
        const inputValues = Array.from(dynamicInputs).map(input => input.value);
        points = inputValues
        
        if (points) {
            fetch('/drawPoints', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ points: points })
            })
            .then(response => response.json())
            .then(data => {
                uploadedImage = data.image_path;

                // Clear the image container before appending the new image
                imageContainer.innerHTML = '';
                
                // Append the new image to the container
                const imgElement = document.createElement('img');
                imgElement.src = uploadedImage + '?' + new Date().getTime();
                imgElement.alt = 'Uploaded Image';
                imageContainer.appendChild(imgElement);
            })
            .catch(error => console.error('Error predicting', error))
        }
    })
    
    addInput.addEventListener('click', () => {
        const newInputContainer = document.createElement('div');
        newInputContainer.className = 'dynamic-input-container';
    
        // Create new input element
        const newInput1 = document.createElement('input');
        newInput1.type = 'text';
        newInput1.className = 'dynamic-input';
        newInput1.placeholder = '2 integers: e.g. x1,y1';
        
        const newInput2 = document.createElement('input');
        newInput2.type = 'text';
        newInput2.className = 'dynamic-input';
        newInput2.placeholder = '1 integers: e.g. 0';
        
        const hr = document.createElement('hr');
    
        const removeButton = document.createElement('button');
        removeButton.type = 'button'
        removeButton.className = 'remove-button';
        removeButton.textContent = 'Remove Field';
        removeButton.addEventListener('click', () => {
            inputContainer.removeChild(newInputContainer);
        });
    
        // Append new input element to container
        newInputContainer.appendChild(removeButton);
        newInputContainer.appendChild(newInput1);
        newInputContainer.appendChild(newInput2);
        newInputContainer.appendChild(hr);
    
        // Append new field container to main container
        inputContainer.appendChild(newInputContainer);
    });

    // Predict Everything
    predictButton.addEventListener('click', () => {
        const values = boxInput.value.split(',').map(Number);
    })
});


