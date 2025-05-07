document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed.'); // <<< ADDED LOG

    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.getElementById('sidebarToggle');

    console.log('Setting up sidebar toggle functionality...'); // <<< ADDED LOG
    console.log('Sidebar elements obtained:', { // <<< ADDED LOG
        sidebar: sidebar ? 'Found' : 'MISSING',
        mainContent: mainContent ? 'Found' : 'MISSING',
        toggle: sidebarToggle ? 'Found' : 'MISSING'
    });

    // --- Sidebar Toggle Functionality ---
    if (sidebarToggle && sidebar && mainContent) {
        console.log('Adding click listener to sidebar toggle...'); // <<< ADDED LOG
        sidebarToggle.addEventListener('click', () => {
            console.log('Sidebar toggle clicked.'); // <<< ADDED LOG
            document.body.classList.toggle('sidebar-collapsed');
        });
    }

    // --- Custom Search Functionality (API Based) ---
    console.log('Setting up custom search functionality...'); // <<< ADDED LOG
    const customSearchButton = document.getElementById('custom-search-button');
    const customSearchInput = document.getElementById('custom-search-input');
    const generatedSqlDiv = document.getElementById('generated-sql');
    const customSearchResultsDiv = document.getElementById('custom-search-results');
    console.log('Search elements obtained:', { // <<< ADDED LOG
        button: customSearchButton ? 'Found' : 'MISSING',
        input: customSearchInput ? 'Found' : 'MISSING',
        sqlDiv: generatedSqlDiv ? 'Found' : 'MISSING',
        resultsDiv: customSearchResultsDiv ? 'Found' : 'MISSING'
    });

    if (customSearchButton && customSearchInput && generatedSqlDiv && customSearchResultsDiv) {
        console.log('Adding click listener to search button...'); // <<< ADDED LOG
        customSearchButton.addEventListener('click', async () => {
            console.log('Search button clicked.'); // <<< ADDED LOG
            const query = customSearchInput.value.trim();
            if (!query) {
                alert('Please enter a search query.');
                return;
            }

            // Clear previous results and show loading indicator (optional)
            generatedSqlDiv.textContent = 'Generating SQL...';
            customSearchResultsDiv.innerHTML = 'Loading results...'; // Use innerHTML if displaying HTML

            try {
                console.log(`Attempting to fetch from API with query: "${query}"`); // <<< ADDED LOG
                // --- CORRECTED FETCH CALL ---
                const response = await fetch('http://127.0.0.1:5001/api/chat-to-sql', { // Use full URL with correct port and path
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ naturalLanguage: query }), // Use correct key 'naturalLanguage'
                });

                if (!response.ok) {
                    // Handle HTTP errors (like 500 Internal Server Error)
                    const errorData = await response.json().catch(() => ({ error: 'Failed to parse error response' }));
                    throw new Error(`API Error (${response.status}): ${errorData.error || response.statusText}`);
                }

                const data = await response.json();
                console.log("API Response:", data);

                // Display Generated SQL
                generatedSqlDiv.textContent = data.sql || 'No SQL generated.';

                // Display Results (Format as a table)
                if (data.results && data.results.length > 0) {
                    let tableHTML = '<table class="results-table"><thead><tr>';
                    // Assume results is an array of objects, get headers from the first object
                    const headers = Object.keys(data.results[0]);
                    headers.forEach(header => tableHTML += `<th>${header}</th>`);
                    tableHTML += '</tr></thead><tbody>';

                    data.results.forEach(row => {
                        tableHTML += '<tr>';
                        headers.forEach(header => {
                             // Basic sanitization for display
                            const cellValue = String(row[header] !== null && row[header] !== undefined ? row[header] : '');
                            const sanitizedValue = cellValue.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                            tableHTML += `<td>${sanitizedValue}</td>`;
                        });
                        tableHTML += '</tr>';
                    });

                    tableHTML += '</tbody></table>';
                    customSearchResultsDiv.innerHTML = tableHTML;
                } else {
                    customSearchResultsDiv.textContent = 'No matching stocks found.';
                }

            } catch (error) {
                console.error('Error fetching custom search results:', error);
                generatedSqlDiv.textContent = 'Error generating SQL.';
                customSearchResultsDiv.textContent = `Error: ${error.message}`; // Display error message to user
            }
        });
    } else {
        // Log if any element was missing (this might help!)
        console.error("Could not find one or more required custom search elements. Listener not added.", {
            button: !!customSearchButton,
            input: !!customSearchInput,
            sqlDiv: !!generatedSqlDiv,
            resultsDiv: !!customSearchResultsDiv
        });
    }

    // --- Screener Card Filtering ---
    console.log('Setting up screener card filtering functionality...'); // <<< ADDED LOG
    const searchInput = document.getElementById('custom-search-input');
    const screenerCards = document.querySelectorAll('.category-item'); 
    console.log('Screener card elements obtained:', { // <<< ADDED LOG
        input: searchInput ? 'Found' : 'MISSING',
        cards: screenerCards.length > 0 ? 'Found' : 'MISSING'
    });

    if (searchInput && screenerCards.length > 0) {
        console.log('Adding input listener to search input...'); // <<< ADDED LOG
        searchInput.addEventListener('input', () => {
            console.log('Search input changed.'); // <<< ADDED LOG
            const searchTerm = searchInput.value.trim().toLowerCase();
            filterScreenerCards(searchTerm);
        });
        
        function filterScreenerCards(searchTerm) {
            screenerCards.forEach(card => {
                const titleElement = card.querySelector('h4');
                if (titleElement) {
                    const title = titleElement.textContent.trim().toLowerCase();
                    if (title.includes(searchTerm)) {
                        card.style.display = ''; 
                    } else {
                        card.style.display = 'none'; 
                    }
                }
            });
            
            const categoryBoxes = document.querySelectorAll('.category-box');
            categoryBoxes.forEach(box => {
                const visibleItems = box.querySelectorAll('.category-item[style*="display: none;"]');
                const totalItems = box.querySelectorAll('.category-item');
                if (visibleItems.length === totalItems.length && totalItems.length > 0) {
                    box.style.display = 'none'; 
                } else {
                     box.style.display = ''; 
                }
            });
        }
    }
});
