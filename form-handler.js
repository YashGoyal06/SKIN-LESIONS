document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('image');
    const fileUploadText = document.querySelector('.file-upload-text');
    const uploadMessage = document.getElementById('upload-message');

    fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
            const maxSize = 20 * 1024 * 1024; // 20MB in bytes

            // Validate file type and size
            if (!validTypes.includes(file.type)) {
                alert('Please upload an image in JPG, JPEG, or PNG format.');
                fileInput.value = '';
                fileUploadText.textContent = 'Choose Image';
                uploadMessage.style.display = 'none';
                return;
            }

            if (file.size > maxSize) {
                alert('File size exceeds 20MB. Please upload a smaller image.');
                fileInput.value = '';
                fileUploadText.textContent = 'Choose Image';
                uploadMessage.style.display = 'none';
                return;
            }

            // Update file upload text with file name
            fileUploadText.textContent = file.name;

            // Show upload successful message
            uploadMessage.innerHTML = `
                <span class="message-text">Upload Successful: ${file.name}</span>
                <button class="close-btn" aria-label="Close message">×</button>
            `;
            uploadMessage.style.display = 'flex';
            uploadMessage.classList.add('show');

            // Add event listener to close button
            const closeBtn = uploadMessage.querySelector('.close-btn');
            closeBtn.addEventListener('click', () => {
                uploadMessage.style.display = 'none';
                uploadMessage.classList.remove('show');
            });
        } else {
            fileUploadText.textContent = 'Choose Image';
            uploadMessage.style.display = 'none';
            uploadMessage.classList.remove('show');
        }
    });
});