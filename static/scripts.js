// Run when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    console.log("Loaded gridData:", gridData);

    // Toggle sidebar menu (furniture categories)
    window.toggleMenu = function () {
        const sidebar = document.getElementById('sidebar');
        const arrow = document.getElementById('menu-arrow');
        const isHidden = sidebar.classList.contains('hidden');
        
        sidebar.classList.toggle('hidden'); // Show/hide sidebar
        arrow.classList.toggle('rotate', !isHidden); // Rotate arrow if opening

        // If opening sidebar, collapse all furniture categories
        if (!isHidden) {
            const allCategories = sidebar.querySelectorAll('.category-items');
            allCategories.forEach(section => {
                section.style.display = 'none';
            });
        }
    };

    // Expand/collapse a furniture category
    window.toggleCategory = function (header) {
        const items = header.nextElementSibling;
        const isOpen = items.style.display === 'flex';
        items.style.display = isOpen ? 'none' : 'flex';
    };

    const canvas = document.getElementById('canvas');
    if (!canvas) {
        console.error("Canvas element not found.");
        return;
    }

    // Track selected furniture and drag state
    let selectedItem = null;
    let isDragging = false;
    let dragOffsetX = 0;
    let dragOffsetY = 0;
    let previewImg = null;

    // Handle selecting furniture already on canvas
    canvas.addEventListener('click', function (e) {
        const clicked = e.target;
        if (clicked.classList.contains('furniture-placed')) {
            if (selectedItem) selectedItem.classList.remove('selected');
            selectedItem = clicked;
            selectedItem.classList.add('selected');
        } else {
            if (selectedItem) selectedItem.classList.remove('selected');
            selectedItem = null;
        }
    });

    // Remove selected furniture from canvas
    window.removeRoom = function () {
        if (selectedItem) {
            selectedItem.remove();
            selectedItem = null;
        } else {
            alert("Please select a furniture item to remove.");
        }
    };

    // Rotate selected furniture item
    window.rotateSelected = function () {
        if (!selectedItem) {
            alert("Please select a furniture item to rotate.");
            return;
        }
        const current = parseInt(selectedItem.dataset.rotation || "0");
        const next = (current + 90) % 360;
        selectedItem.dataset.rotation = next;
        selectedItem.style.transform = `rotate(${next}deg)`;
    };

    // Handle dragging placed furniture
    canvas.addEventListener('mousedown', function (e) {
        const target = e.target;
        if (target.classList.contains('furniture-placed')) {
            isDragging = true;
            selectedItem = target;
            selectedItem.classList.add('selected');

            // Calculate cursor offset inside the furniture item
            const rect = selectedItem.getBoundingClientRect();
            dragOffsetX = e.clientX - rect.left;
            dragOffsetY = e.clientY - rect.top;

            e.preventDefault(); // Prevent image drag behavior
        }
    });

    // Move dragged furniture or preview image with mouse
    document.addEventListener('mousemove', function (e) {
        if (isDragging && selectedItem) {
            const canvasRect = canvas.getBoundingClientRect();
            let newLeft = e.clientX - canvasRect.left - dragOffsetX;
            let newTop = e.clientY - canvasRect.top - dragOffsetY;

            selectedItem.style.left = `${newLeft}px`;
            selectedItem.style.top = `${newTop}px`;
        }

        // Move preview image during drag
        if (previewImg) {
            const canvasRect = canvas.getBoundingClientRect();
            const x = e.clientX - canvasRect.left;
            const y = e.clientY - canvasRect.top;
            previewImg.style.left = (x - previewImg.offsetWidth / 2) + 'px';
            previewImg.style.top = (y - previewImg.offsetHeight / 2) + 'px';
        }
    });

    // Stop dragging on mouse up
    document.addEventListener('mouseup', function () {
        isDragging = false;
    });

    // Handle furniture item selection from sidebar
    document.querySelectorAll('.furniture').forEach(item => {
        item.addEventListener('dragstart', e => e.preventDefault()); // Disable native drag

        item.addEventListener('mousedown', function (e) {
            // Save furniture data in dataset
            const data = {
                src: item.src,
                width: item.getAttribute('data-width'),
                height: item.getAttribute('data-height')
            };
            item.dataset.furnitureData = JSON.stringify(data);

            if (selectedItem) {
                selectedItem.classList.remove('selected');
                selectedItem = null;
            }

            // Create a transparent preview of the furniture to follow the cursor
            previewImg = document.createElement('img');
            previewImg.src = data.src;
            previewImg.classList.add('furniture-placed');
            previewImg.style.position = 'absolute';
            previewImg.style.width = parseInt(data.width) * 20 + 'px';
            previewImg.style.height = parseInt(data.height) * 20 + 'px';
            previewImg.style.pointerEvents = 'none';
            previewImg.style.opacity = '0.6';

            const canvasRect = canvas.getBoundingClientRect();
            const x = e.clientX - canvasRect.left;
            const y = e.clientY - canvasRect.top;

            previewImg.style.left = (x - (parseInt(data.width) * 10)) + 'px';
            previewImg.style.top = (y - (parseInt(data.height) * 10)) + 'px';

            canvas.appendChild(previewImg);
        });
    });

    // Finalize furniture placement on mouse release
    canvas.addEventListener('mouseup', function (e) {
        const dragged = document.querySelector('[data-furniture-data]');
        if (dragged && previewImg) {
            // Drop preview as real item
            previewImg.style.opacity = '1';
            previewImg.style.pointerEvents = 'auto';
            previewImg.dataset.rotation = "0";
            previewImg.style.transform = "rotate(0deg)";
            previewImg = null;
            delete dragged.dataset.furnitureData;
        } else if (previewImg) {
            // Cancel placement if not dropped
            previewImg.remove();
            previewImg = null;
        }
    });

    // Save room layout to server
    window.saveRoom = function () {
        const items = canvas.querySelectorAll('.furniture-placed');
        const layout = [];

        // Collect data from each placed item
        items.forEach(item => {
            layout.push({
                src: item.src,
                left: item.style.left,
                top: item.style.top,
                width: item.style.width,
                height: item.style.height,
                rotation: item.dataset.rotation || "0"
            });
        });

        // Send layout to backend using Fetch API
        fetch(`/save_room/${roomId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ layout })
        })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                console.error('Failed to save room:', data.message || 'Unknown error');
            }
        })
        .catch(err => {
            alert('An error occurred while saving.');
            console.error(err);
        });
    };

    // Load room layout (if already saved)
    if (Array.isArray(gridData)) {
        gridData.forEach(item => {
            const img = document.createElement('img');
            img.src = item.src;
            img.classList.add('furniture-placed');
            img.style.position = 'absolute';
            img.style.left = item.left;
            img.style.top = item.top;
            img.style.width = item.width;
            img.style.height = item.height;
            img.dataset.rotation = item.rotation || "0";
            img.style.transform = `rotate(${img.dataset.rotation}deg)`;
            canvas.appendChild(img);
        });
    }
});

// Rename room by sending new name to the server
window.renameRoom = function () {
    const input = document.getElementById('room-name-input');
    const newName = input.value.trim();

    if (!newName) {
        alert("Room name cannot be empty.");
        return;
    }

    // Send rename request to server
    fetch(`/rename_room/${roomId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ new_name: newName })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            document.title = `Edit Room - ${newName}`; // Update page title
            // Optional: update UI elsewhere if needed
        } else {
            alert("Failed to rename room.");
        }
    })
    .catch(err => {
        alert("An error occurred.");
        console.error(err);
    });
};
