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
    const predictEverything = document.getElementById('predictEverything')

    // Predict Box
    const predictBox = document.getElementById('predictBox')

    // Predict Text
    const textInput = document.getElementById('textInput')
    const predictText = document.getElementById('predictText')
    
    // Predict Points
    const predictPoints = document.getElementById('predictPoints')

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
    
    // Add inputs for Points
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
    predictEverything.addEventListener('click', () => {
        fetch('/predictEverything', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
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
    })

    // Predict Box
    predictBox.addEventListener('click', () => {
        const values = boxInput.value.split(',').map(Number);
        if (values.length === 4) {
            boxCoordinates = values;
        }

        if (boxCoordinates) {
            fetch('/predictBox', {
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
            .catch(error => console.error('Error predicting', error))
        }
    });

    // Predict Text
    predictText.addEventListener('click', () => {
        const values = textInput.value;
        if (values.length !== null) {
            text = values;
        }

        if (text) {
            fetch('/predictText', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
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
    });

    // Predict Points
    predictPoints.addEventListener('click', () => {
        const dynamicInputs = form.querySelectorAll('.dynamic-input');
        const inputValues = Array.from(dynamicInputs).map(input => input.value);
        points = inputValues
        
        if (points) {
            fetch('/predictPoints', {
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
    // 


});


