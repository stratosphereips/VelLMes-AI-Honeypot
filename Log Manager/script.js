// Function to fetch SSH session data from the Flask server
function fetchSSH_Sessions() {
    fetch('http://127.0.0.1:5000/ssh_sessions')
        .then(response => response.json())
        .then(data => {
            displaySSHSessions(data);
        })
        .catch(error => {
            console.error('Error fetching SSH sessions:', error);
        });
}

// Function to fetch shelLM sessions data from the Flask server
function fetchShelLM_Sessions() {
    fetch('http://127.0.0.1:5000/shellm_sessions')
        .then(response => response.json())
        .then(data => {
            displayshelLMSessions(data);
        })
        .catch(error => {
            console.error('Error fetching shelLM sessions:', error);
        });
}

// Function to fetch Commands data from the Flask server
function fetchCommands() {
    fetch('http://127.0.0.1:5000/commands')
        .then(response => response.json())
        .then(data => {
            displayCommands(data);
        })
        .catch(error => {
            console.error('Error fetching Commands:', error);
        });
}

// Function to fetch Answers data from the Flask server
function fetchAnswers() {
    fetch('http://127.0.0.1:5000/answers')
        .then(response => response.json())
        .then(data => {
            displayAnswers(data);
        })
        .catch(error => {
            console.error('Error fetching Answers:', error);
        });
}

// Function to display SSH sessions in the table
function displaySSHSessions(sessions) {
    console.log("Sessions data received:", sessions);

    const table = document.getElementById("ssh-sessions-table"); // Reference to the table
    const tableBody = document.getElementById("ssh-sessions-table-body");

    if (!table || !tableBody) {
        console.error("Table or table body with ID 'ssh-sessions-table' or 'ssh-sessions-table-body' not found.");
        return;
    }

    // Make sure the table is visible
    table.style.display = "table";  // Unhide the table

    // Clear previous entries
    tableBody.innerHTML = "";

    // Check if 'sessions' is an array and contains valid data
    if (Array.isArray(sessions) && sessions.length > 0) {
        sessions.forEach((session, index) => {
            console.log(`Processing session ${index}:`, session);

            if (!Array.isArray(session) || session.length < 7) {
                console.error("Invalid session data:", session);
                return;
            }

            const row = document.createElement("tr");

            const idCell = document.createElement("td");
            idCell.textContent = session[0];

            const usernameCell = document.createElement("td");
            usernameCell.textContent = session[1];

            const timeDateCell = document.createElement("td");
            timeDateCell.textContent = session[2];

            const srcIPCell = document.createElement("td");
            srcIPCell.textContent = session[3];

            const dstIPCell = document.createElement("td");
            dstIPCell.textContent = session[4];

            const dstPortCell = document.createElement("td");
            dstPortCell.textContent = session[6];

            row.appendChild(idCell);
            row.appendChild(usernameCell);
            row.appendChild(timeDateCell);
            row.appendChild(srcIPCell);
            row.appendChild(dstIPCell);
            row.appendChild(dstPortCell);

            tableBody.appendChild(row);
        });

        console.log("Table populated successfully.");
    } else {
        console.error("Invalid data structure received:", sessions);
    }
}


// Function to display SSH sessions in the table
function displayshelLMSessions(sessions) {
    console.log("Sessions data received:", sessions);

    const table = document.getElementById("shellm-sessions-table"); // Reference to the table
    const tableBody = document.getElementById("shellm-sessions-table-body");

    if (!table || !tableBody) {
        console.error("Table or table body with ID 'shellm-sessions-table' or 'shellm-sessions-table-body' not found.");
        return;
    }

    // Make sure the table is visible
    table.style.display = "table";  // Unhide the table

    // Clear previous entries
    tableBody.innerHTML = "";

    // Check if 'sessions' is an array and contains valid data
    if (Array.isArray(sessions) && sessions.length > 0) {
        sessions.forEach((session, index) => {
            console.log(`Processing session ${index}:`, session);

            if (!Array.isArray(session) || session.length < 6) {
                console.error("Invalid session data:", session);
                return;
            }

            const row = document.createElement("tr");

            const idCell = document.createElement("td");
            idCell.textContent = session[0];
            idCell.style.cursor = "pointer";
            idCell.addEventListener("click", () => fetchAndDisplayCommandsAnswers(session[0]));

            const ssh_session_idCell = document.createElement("td");
            ssh_session_idCell.textContent = session[1];

            const modelCell = document.createElement("td");
            modelCell.textContent = session[2];

            const start_timeCell = document.createElement("td");
            start_timeCell.textContent = session[3];

            const end_timeCell = document.createElement("td");
            end_timeCell.textContent = session[4];

            const attacker_idCell = document.createElement("td");
            attacker_idCell.textContent = session[5];

            row.appendChild(idCell);
            row.appendChild(ssh_session_idCell);
            row.appendChild(modelCell);
            row.appendChild(start_timeCell);
            row.appendChild(end_timeCell);
            row.appendChild(attacker_idCell);

            tableBody.appendChild(row);
        });

        console.log("Table populated successfully.");
    } else {
        console.error("Invalid data structure received:", sessions);
    }
}

// Function to display SSH sessions in the table
function displayCommands(sessions) {
    console.log("Commands data received:", sessions);

    const table = document.getElementById("commands-table"); // Reference to the table
    const tableBody = document.getElementById("commands-table-body");

    if (!table || !tableBody) {
        console.error("Table or table body with ID 'commands-table' or 'commands-table-body' not found.");
        return;
    }

    // Make sure the table is visible
    table.style.display = "table";  // Unhide the table

    // Clear previous entries
    tableBody.innerHTML = "";

    // Check if 'sessions' is an array and contains valid data
    if (Array.isArray(sessions) && sessions.length > 0) {
        sessions.forEach((session, index) => {
            console.log(`Processing command ${index}:`, session);

            if (!Array.isArray(session) || session.length < 3) {
                console.error("Invalid commands data:", session);
                return;
            }

            const row = document.createElement("tr");

            const idCell = document.createElement("td");
            idCell.textContent = session[0];

            const shellm_session_idCell = document.createElement("td");
            shellm_session_idCell.textContent = session[1];

            const commandCell = document.createElement("td");
            commandCell.textContent = session[2];

            row.appendChild(idCell);
            row.appendChild(shellm_session_idCell);
            row.appendChild(commandCell);

            tableBody.appendChild(row);
        });

        console.log("Table populated successfully.");
    } else {
        console.error("Invalid data structure received:", sessions);
    }
}

// Function to display SSH sessions in the table
function displayAnswers(sessions) {
    console.log("Answers data received:", sessions);

    const table = document.getElementById("answers-table"); // Reference to the table
    const tableBody = document.getElementById("answers-table-body");

    if (!table || !tableBody) {
        console.error("Table or table body with ID 'answers-table' or 'answers-table-body' not found.");
        return;
    }

    // Make sure the table is visible
    table.style.display = "table";  // Unhide the table

    // Clear previous entries
    tableBody.innerHTML = "";

    // Check if 'sessions' is an array and contains valid data
    if (Array.isArray(sessions) && sessions.length > 0) {
        sessions.forEach((session, index) => {
            console.log(`Processing answer ${index}:`, session);

            if (!Array.isArray(session) || session.length < 3) {
                console.error("Invalid answer data:", session);
                return;
            }

            const row = document.createElement("tr");

            const idCell = document.createElement("td");
            idCell.textContent = session[0];

            const command_idCell = document.createElement("td");
            command_idCell.textContent = session[1];

            const answerCell = document.createElement("td");
            answerCell.textContent = session[2];

            row.appendChild(idCell);
            row.appendChild(command_idCell);
            row.appendChild(answerCell);

            tableBody.appendChild(row);
        });

        console.log("Table populated successfully.");
    } else {
        console.error("Invalid data structure received:", sessions);
    }
}

// Function to fetch and display commands and answers for a shellm session
function fetchAndDisplayCommandsAnswers(shellmSessionID) {
    console.log("Fetching commands and answers for ShellM Session ID:", shellmSessionID);

    fetch(`http://127.0.0.1:5000/commands_answers/${shellmSessionID}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            const tableBody = document.getElementById("commands-answers-table-body");
            const commandsAnswersTable = document.getElementById("commands-answers-table");

            if (!tableBody || !commandsAnswersTable) {
                console.error("Commands and Answers table elements not found in the DOM.");
                return;
            }

            // Clear previous entries
            tableBody.innerHTML = "";

            // Show the table
            commandsAnswersTable.style.display = "table";

            // Populate the table with the received data
            if (Array.isArray(data) && data.length > 0) {
                data.forEach((entry) => {
                    const row = document.createElement("tr");

                    // Create and populate cells
                    const commandIDCell = document.createElement("td");
                    commandIDCell.textContent = entry.command_id || "N/A";

                    const commandCell = document.createElement("td");
                    commandCell.textContent = entry.command || "N/A";

                    const answerIDCell = document.createElement("td");
                    answerIDCell.textContent = entry.answer_id || "N/A";

                    const answerCell = document.createElement("td");
                    answerCell.textContent = entry.answer || "N/A";

                    // Append cells to the row
                    row.appendChild(commandIDCell);
                    row.appendChild(commandCell);
                    row.appendChild(answerIDCell);
                    row.appendChild(answerCell);

                    // Append the row to the table body
                    tableBody.appendChild(row);
                });
            } else {
                // If no data is found, show a "No data available" message
                const row = document.createElement("tr");
                const noDataCell = document.createElement("td");
                noDataCell.textContent = "No commands or answers found for this session.";
                noDataCell.colSpan = 4;
                row.appendChild(noDataCell);
                tableBody.appendChild(row);
            }
        })
        .catch((error) => console.error("Error fetching commands and answers:", error));
}

// Function to hide all tables
function hideAllTables() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => table.style.display = 'none');
}

// Add event listeners to the buttons
document.getElementById('sshSessionsBtn').addEventListener('click', () => {
    hideAllTables();
    fetchSSH_Sessions();
});
document.getElementById('shelLM_SessionsBtn').addEventListener('click', () => {
    hideAllTables();
    fetchShelLM_Sessions();
});
document.getElementById('commandsBtn').addEventListener('click', () => {
    hideAllTables();
    fetchCommands();
});
document.getElementById('answersBtn').addEventListener('click', () => {
    hideAllTables();
    fetchAnswers();
});

// Function to handle ID click
function handleIDClick(shellmSessionID) {
    console.log("ShellM Session ID clicked:", shellmSessionID);

    const commandsAnswersSection = document.getElementById("commands-answers-section");
    commandsAnswersSection.style.display = "block"; // Show the new button

    const commandsAnswersBtn = document.getElementById("commandsAnswersBtn");
    commandsAnswersBtn.onclick = () => fetchAndDisplayCommandsAnswers(shellmSessionID); // Attach handler
}

// Ensure the page is ready for actions
document.addEventListener("DOMContentLoaded", () => {
    console.log("Log Manager Dashboard ready.");
});
