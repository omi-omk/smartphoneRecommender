document.addEventListener('DOMContentLoaded', () => {
    // Update slider values
    document.querySelectorAll('input[type="range"]').forEach(slider => {
        slider.addEventListener('input', (e) => {
            e.target.nextElementSibling.textContent = e.target.value;
        });
    });

    // Drag and drop functionality
    const priorityList = document.getElementById('priorityList');
    let draggingElement = null;

    document.querySelectorAll('.priority-item').forEach(item => {
        item.addEventListener('dragstart', (e) => {
            draggingElement = item;
            item.classList.add('dragging');
        });

        item.addEventListener('dragend', () => {
            draggingElement.classList.remove('dragging');
            draggingElement = null;
        });
    });

    priorityList.addEventListener('dragover', (e) => {
        e.preventDefault();
        const afterElement = getDragAfterElement(priorityList, e.clientY);
        const currentElement = draggingElement;
        
        if (afterElement == null) {
            priorityList.appendChild(currentElement);
        } else {
            priorityList.insertBefore(currentElement, afterElement);
        }
    });

    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.priority-item:not(.dragging)')];

        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    // Form submission
    document.getElementById('submitBtn').addEventListener('click', async () => {
        const preferences = [
            parseInt(document.getElementById('design').value),
            parseInt(document.getElementById('display').value),
            parseInt(document.getElementById('software').value),
            parseInt(document.getElementById('performance').value),
            parseInt(document.getElementById('battery').value),
            parseInt(document.getElementById('camera').value)
        ];

        const budget = parseInt(document.getElementById('budget').value);
        
        // Calculate priority weights (6 = highest, 1 = lowest)
        const priorityItems = document.querySelectorAll('.priority-item');
        const priorityList = Array.from(priorityItems).map(item => 
            6 - Array.from(priorityItems).indexOf(item)
        );

        try {
            const response = await fetch('/get_recommendations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    preferences,
                    budget,
                    priority_list: priorityList
                })
            });

            const data = await response.json();
            
            if (data.success) {
                if (data.recommendations.length === 0) {
                    showError("No smartphones found within your budget. Please try increasing your budget.");
                } else {
                    displayResults(data.recommendations);
                }
            } else {
                showError('Error: ' + data.error);
            }
        } catch (error) {
            showError('Error connecting to server');
        }
    });

    function showError(message) {
        const resultsContainer = document.getElementById('results');
        const recommendationsDiv = resultsContainer.querySelector('.recommendations');
        
        recommendationsDiv.innerHTML = `
            <div class="error-message">
                <p>${message}</p>
            </div>
        `;
        
        resultsContainer.classList.remove('hidden');
    }

    function displayResults(phones) {
        const resultsContainer = document.getElementById('results');
        const recommendationsDiv = resultsContainer.querySelector('.recommendations');
        
        recommendationsDiv.innerHTML = phones.map(phone => `
            <div class="phone-card">
                <img src="${phone.img_links}" alt="${phone.mobiles}">
                <div class="phone-info">
                    <div class="phone-name">${phone.mobiles}</div>
                    <div class="phone-price">Price: ₹${phone.b_Price.toLocaleString()}</div>
                    
                    <div class="key-specs">
                        <h3>Key Specifications</h3>
                        <div class="specs-list">
                            <div>Display: ${phone.k_Display}</div>
                            <div>Processor: ${phone.k_Processor}</div>
                            <div>Front Camera: ${phone.k_Front_Camera}</div>
                            <div>Rear Camera: ${phone.k_Rear_Camera}</div>
                            <div>RAM: ${phone.k_RAM}</div>
                            <div>Storage: ${phone.k_Storage}</div>
                            <div>Battery: ${phone.k_Battery_Capacity}</div>
                            <div>OS: ${phone.k_OS}</div>
                        </div>
                    </div>
                    
                    <div class="action-buttons">
                        <a href="${phone.best_buy_links}" target="_blank" class="buy-btn">Buy Now</a>
                        <a href="/specifications?phones=${phone.index_num}" class="specs-btn">Full Specifications</a>
                    </div>
                </div>
            </div>
        `).join('');

        // Add compare button if there are 2 phones
        if (phones.length === 2) {
            const compareButton = document.createElement('div');
            compareButton.className = 'compare-button-container';
            compareButton.innerHTML = `
                <a href="/compare?phones=${phones[0].index_num}&phones=${phones[1].index_num}" class="compare-btn">
                    Compare These Phones
                </a>
            `;
            recommendationsDiv.appendChild(compareButton);
        }

        resultsContainer.classList.remove('hidden');
    }
});