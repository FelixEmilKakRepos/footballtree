var tippingData = {};
var oldActiveMatchNumber;

async function updateData() {
    // Include the last data version in the request headers
    var headers = new Headers();
    headers.append('Last-Data-Update', data['LastUpdate']);

    await fetch('/update_data', {
        headers: headers,
    })
        .then((response) => response.json())
        .then((updatedData) => {
            console.log('Updated data:', updatedData);

            // Update variables in JavaScript
            for (var key in updatedData) {
                if (updatedData.hasOwnProperty(key)) {
                    data[key] = updatedData[key];
                }
            }
        })
        .catch((error) => console.error('Error fetching data:', error));

    await fetch('/tipping_data', {
        method: 'GET',
    })
        .then((response) => response.json())
        .then((updatedtippingData) => {
            console.log('Updated tipping data:', updatedtippingData);
            tippingData = updatedtippingData;
        })
        .catch((error) => console.error('Error fetching tipping data:', error));

    document.title = data['websiteTitle'];
    document.getElementById('websiteTitle').textContent = data['websiteTitle'];

    console.log('Tipping data:', tippingData);

    if (currentlyTyping == false && tippingData['name'] != null) {
        document.getElementById('name-input').value = tippingData['name'];
    }

    await generateDropdownData();
}

function generateDropdownData() {
    var dropdown = document.getElementById('game-select');

    // Store the currently selected value
    var selectedValue = dropdown.value;

    console.log('Active match number:', data['activeMatchNumber']);
    console.log('Old active match number:', oldActiveMatchNumber);

    if (data['activeMatchNumber'] == oldActiveMatchNumber) {
        return;
    }

    while (dropdown.firstChild) {
        dropdown.removeChild(dropdown.firstChild);
    }

    var disabledOptions = [];
    var enabledOptions = [];

    for (var i = 0; i < data['Matches'].length; i++) {
        let group;
        var option = document.createElement('option');
        matchData = data['Matches'][i];

        if (
            data['activeMatchNumber'] < -1 ||
            i < data['activeMatchNumber'] + 1
        ) {
            option.style.color = 'gray';
            disabledOptions.push(option);
        } else {
            enabledOptions.push(option);
        }

        if (matchData[4] == 1) {
            group = 'Gruppe A';
        } else if (matchData[4] == 2) {
            group = 'Gruppe B';
        } else {
            group = 'Gruppe nicht definiert';
        }

        option.textContent = `${i + 1}. ${group}: ${matchData[0]} vs ${
            matchData[1]
        }`;

        // Set the selected option if it matches the currently selected value
        if (option.textContent === selectedValue) {
            option.selected = true;
        }
    }

    if (!(data['activeMatchNumber'] < -1)) {
        var KOdivider = document.createElement('option');
        KOdivider.disabled = true;
        KOdivider.textContent = '';
        enabledOptions.push(KOdivider);
    } else {
        var KOdivider = document.createElement('option');
        KOdivider.disabled = true;
        KOdivider.textContent = '';
        disabledOptions.push(KOdivider);
    }

    if (data['KOMatches'] != null && data['KOMatches'].length != 0) {
        for (var i = 0; i < data['KOMatches'].length; i++) {
            if (
                data['KOMatches'][i][0] == null ||
                data['KOMatches'][i][1] == null
            ) {
                continue;
            }

            let group;
            var option = document.createElement('option');
            matchData = data['KOMatches'][i];

            group = i + 1 + '. K.O. Spiel';

            option.textContent = `${group}: ${matchData[0]} vs ${matchData[1]}`;

            if (
                ((data['activeMatchNumber'] < -1 &&
                    data['activeMatchNumber'] > -99) ||
                    data['activeMatchNumber'] < (i + 99) * -1) &&
                data['pauseMode'] != 0
            ) {
                option.style.color = 'gray';
                disabledOptions.push(option);
            } else {
                enabledOptions.push(option);
            }

            // Set the selected option if it matches the currently selected value
            if (option.textContent === selectedValue) {
                option.selected = true;
            }
        }

        if (
            !(data['activeMatchNumber'] < -1 && data['activeMatchNumber'] > -99)
        ) {
            var finalDivider = document.createElement('option');
            finalDivider.disabled = true;
            finalDivider.textContent = '';
            enabledOptions.push(finalDivider);
        } else {
            var finalDivider = document.createElement('option');
            finalDivider.disabled = true;
            finalDivider.textContent = '';
            disabledOptions.push(finalDivider);
        }
    }

    if (data['finalMatches'] != null && data['finalMatches'].length != 0) {
        for (var i = 0; i < data['finalMatches'].length; i++) {
            if (
                data['finalMatches'][i][0] == null ||
                data['finalMatches'][i][1] == null
            ) {
                continue;
            }

            let group;
            var option = document.createElement('option');
            matchData = data['finalMatches'][i];

            if (i == 0 || i == 1) {
                group = `${i + 1}. Halbfinale`;
            } else if (i == 2) {
                group = 'Spiel um Platz 3';
            } else if (i == 3) {
                group = 'Finale';
            } else {
                group = 'Nicht definiert';
            }

            option.textContent = `${group}: ${matchData[0]} vs ${matchData[1]}`;

            if (
                !(i == 2 && data['pauseMode'] == 2) &&
                !(i == 3 && data['pauseMode'] == 3)
            ) {
                if (
                    Math.abs(data['activeMatchNumber']) > i + 1 &&
                    data['pauseMode'] != 1
                ) {
                    option.style.color = 'gray';
                    disabledOptions.push(option);
                } else {
                    enabledOptions.push(option);
                }
            } else {
                enabledOptions.push(option);
            }

            // Set the selected option if it matches the currently selected value
            if (option.textContent === selectedValue) {
                option.selected = true;
            }
        }
    }

    if (!(data['activeMatchNumber'] < -4) && data['activeMatchNumber'] < -1) {
        var groupDivider = document.createElement('option');
        groupDivider.disabled = true;
        groupDivider.textContent = '';
        enabledOptions.push(groupDivider);
    }

    // Append the enabled options first
    enabledOptions.forEach((option) => {
        dropdown.appendChild(option);
    });

    // Add a dividing line between disabled and enabled options
    var divider = document.createElement('option');
    divider.disabled = true;
    divider.textContent =
        '------------ Bereits gespielt oder im Gange ------------';
    dropdown.appendChild(divider);

    // Append the disabled options last
    disabledOptions.forEach((option) => {
        dropdown.appendChild(option);
    });

    if (!(data['activeMatchNumber'] == oldActiveMatchNumber)) {
        voteForMatch(document.getElementById('game-select').value);
    }

    let voteContainer = document.getElementById('vote-container');
    if (voteContainer == null) {
        voteForMatch(document.getElementById('game-select').value);
    }

    oldActiveMatchNumber = data['activeMatchNumber'];
}

function voteForMatch(match) {
    let matchPlayed = false;
    var matchNumber = match.split('.')[0] - 1;
    var matchData = data['Matches'][matchNumber];

    console.log(match.split(':')[0]);

    if (match.split(':')[0] == 'Spiel um Platz 3') {
        matchNumber = -4;
        matchData = data['finalMatches'][2];
        console.log('Spiele um Platz 3');
    } else if (match.split(':')[0] == 'Finale') {
        matchNumber = -5;
        matchData = data['finalMatches'][3];
    } else if (match.split('.')[1]) {
        if (match.split('.')[1].startsWith(' Halbfinale')) {
            matchNumber = parseInt(match.split('.')[0]) * -1 - 1;
            console.log('Voting for match', matchNumber);
            matchData = data['finalMatches'][Math.abs(matchNumber) - 2];
        } else if (match.split('.')[1].startsWith(' K')) {
            matchData = data['KOMatches'][matchNumber];
            matchNumber = (parseInt(match.split('.')[0]) + 99) * -1;
            console.log('Voting for match', matchNumber);
        }
    }

    if (data['activeMatchNumber'] < -1 && data['activeMatchNumber'] > -99) {
        if (
            (matchNumber == -4 && data['pauseMode'] == 2) ||
            (matchNumber == -5 && data['pauseMode'] == 3)
        ) {
            matchPlayed = false;
        } else if (matchNumber > -1 || matchNumber < -98) {
            matchPlayed = true;
            console.log('Match played 0');
        } else if (
            matchNumber > data['activeMatchNumber'] - 1 &&
            data['pauseMode'] != 1
        ) {
            matchPlayed = true;
            console.log('Match played 1');
        } else if (matchNumber < -99) {
            matchPlayed = true;
            console.log('Match played 2');
        }
    } else if (data['activeMatchNumber'] < -99) {
        if (matchNumber > -1) {
            matchPlayed = true;
            console.log('Match played 3');
        } else if (
            matchNumber > data['activeMatchNumber'] &&
            data['pauseMode'] != 0
        ) {
            matchPlayed = true;
            console.log('Match played 3');
        }
    } else if (matchNumber < data['activeMatchNumber'] + 1) {
        matchPlayed = true;
        console.log('Match played 4');
    }

    let voteContainer = document.getElementById('vote-container');
    if (voteContainer != null) {
        voteContainer.remove();
    }

    voteContainer = document.createElement('div');
    voteContainer.id = 'vote-container';
    voteContainer.classList.add('vote-container');
    if (matchPlayed) {
        voteContainer.classList.add('disabled');
    }

    let title = document.createElement('h2');
    title.textContent = 'Deine Wette für das Spiel:';
    title.classList.add('vote-title');
    voteContainer.appendChild(title);

    let teamsDiv = document.createElement('div');
    teamsDiv.classList.add('teams');
    voteContainer.appendChild(teamsDiv);

    let team1Div = document.createElement('div');
    team1Div.classList.add('names');
    teamsDiv.appendChild(team1Div);

    let team1 = document.createElement('p');
    team1.classList.add('team');
    team1.textContent = matchData[0];
    team1Div.appendChild(team1);

    let goals1 = document.createElement('input');
    goals1.type = 'number';
    goals1.id = 'goals1';
    goals1.placeholder = 'Tore';
    goals1.min = '0';
    goals1.max = '25';
    goals1.addEventListener('input', function () {
        goals1.value = goals1.value.replace(/\D/g, ''); // Remove non-numeric characters
        if (goals1.value > 25) {
            goals1.value = 25;
        }
    });
    if (tippingData['tips'] != null) {
        if (tippingData['tips'][matchNumber] != null) {
            goals1.value = tippingData['tips'][matchNumber]['team1Goals'];
        }
    }
    if (matchPlayed) {
        goals1.disabled = true;
        goals1.classList.add('disabled');
    }

    team1Div.appendChild(goals1);

    let vs = document.createElement('p');
    vs.textContent = 'vs';
    vs.classList.add('vs');
    teamsDiv.appendChild(vs);

    let team2Div = document.createElement('div');
    team2Div.classList.add('names');
    teamsDiv.appendChild(team2Div);

    let team2 = document.createElement('p');
    team2.classList.add('team');
    team2.textContent = matchData[1];
    team2Div.appendChild(team2);

    let goals2 = document.createElement('input');
    goals2.type = 'number';
    goals2.id = 'goals2';
    goals2.placeholder = 'Tore';
    goals2.min = '0';
    goals2.max = '25';
    goals2.addEventListener('input', function () {
        goals2.value = goals2.value.replace(/\D/g, ''); // Remove non-numeric characters
        if (goals2.value > 25) {
            goals2.value = 25;
        }
    });
    if (tippingData['tips'] != null) {
        if (tippingData['tips'][matchNumber] != null) {
            goals2.value = tippingData['tips'][matchNumber]['team2Goals'];
        }
    }
    if (matchPlayed) {
        goals2.disabled = true;
        goals2.classList.add('disabled');
    }
    team2Div.appendChild(goals2);

    generateButton(matchPlayed, voteContainer);

    let message = document.createElement('p');
    message.textContent = '';
    message.id = 'status-message';
    voteContainer.appendChild(message);

    let container = document.getElementsByClassName('content')[0];
    container.appendChild(voteContainer);
}

function handleSubmit() {
    let matchNumber = -1;
    var goals1 = document.getElementById('goals1').value;
    var goals2 = document.getElementById('goals2').value;
    var match = document.getElementById('game-select').value;
    let name = document.getElementById('name-input').value;

    if (name.length < 3) {
        generateErrorMessage('Du musst einen Namen eingeben!');
        return;
    }

    if (match.split('.')[1]) {
        if (match.split('.')[1].startsWith(' Halbfinale')) {
            matchNumber = parseInt(match.split('.')[0]) * -1 - 1;
        } else if (match.split('.')[1].startsWith(' K')) {
            matchData = data['KOMatches'][matchNumber];
            matchNumber = (parseInt(match.split('.')[0]) + 99) * -1;
        } else {
            matchNumber = match.split('.')[0] - 1;
        }
    } else if (match.split(':')[0] == 'Spiel um Platz 3') {
        matchNumber = -4;
    } else if (match.split(':')[0] == 'Finale') {
        matchNumber = -5;
    }

    if (goals1 == '' || goals2 == '') {
        console.log('No goals entered');
        generateErrorMessage(
            'Du musst für beide Teams eine Toranzahl angeben!'
        );
        return;
    }

    console.log('Submitting tipping data for match', matchNumber);

    fetch('/send_tipping_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            matchId: matchNumber,
            team1Goals: goals1,
            team2Goals: goals2,
        }),
    })
        .then((response) => {
            if (response.status != 200) {
                throw response;
            }
            return response.text();
        })
        .then((data) => {
            console.log('Success:', data);
            //updateData();
            generateSuccessMessage(
                'Deine Wette wurde erfolgreich abgeschickt!'
            );
        })
        .catch((error) => {
            console.log(error.text());
            generateErrorMessage('Fehler, bitte versuche es erneut!');
        });
}

function redirectTo(path) {
    window.location.href = path;
}

let messageTimeout;

function showMessage(message, className) {
    let statusMessage = document.getElementById('status-message');
    statusMessage.classList.add(className);
    statusMessage.textContent = message;

    console.log('Message shown');

    console.log(messageTimeout);

    //clearTimeout(messageTimeout);
    messageTimeout = setTimeout(function () {
        console.log('Message hidden');
        statusMessage.classList.add('fade-out');
        setTimeout(function () {
            statusMessage.textContent = '';
            statusMessage.classList.remove(className);
            statusMessage.classList.remove('fade-out');
        }, 1000); // same as the transition duration
    }, 5000);
}

function generateErrorMessage(message) {
    showMessage(message, 'error-message');
}

function generateSuccessMessage(message) {
    showMessage(message, 'success-message');
}

let lastClicked = null;
const COOLDOWN_TIME = 2000; // 10 seconds
function generateButton(matchPlayed, voteContainer) {
    let button = document.createElement('button');
    button.innerText = 'Wette abschicken';
    button.id = 'submit-button';
    if (matchPlayed) {
        button.disabled = true;
        button.classList.add('disabled');
    } else {
        button.onclick = function () {
            let now = Date.now();
            if (lastClicked && now - lastClicked < COOLDOWN_TIME) {
                generateErrorMessage(
                    'Bitte warte einen Moment, bevor du erneut klickst!',
                    'error-message'
                );
            } else {
                lastClicked = now;
                handleSubmit();
            }
        };
    }
    voteContainer.appendChild(button);
}

document.getElementById('returnButton').addEventListener('click', function () {
    redirectTo('/');
});

document.getElementById('game-select').addEventListener('change', function () {
    var selectedMatch = document.getElementById('game-select').value;
    voteForMatch(selectedMatch);
});

var typingTimer;
var doneTypingInterval = 500;

var currentlyTyping = false;

document.getElementById('name-input').addEventListener('input', function () {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(function () {
        var name = document.getElementById('name-input').value;
        fetch('/send_user_name', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userName: name,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        currentlyTyping = false;
    }, doneTypingInterval);
});

document.getElementById('name-input').addEventListener('keydown', function () {
    clearTimeout(typingTimer);
    currentlyTyping = true;
});

updateData();
setInterval(updateData, 10000);
