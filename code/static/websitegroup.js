function generateTables() {
    var tablesContainer = document.getElementById("tablesContainer");
    tablesContainer.innerHTML = "";

    var tableCount = 2;
    var teamCount = data.Teams.length;
    if (teamCount % 2 != 0) {
        var entriesTable1 = Math.ceil(teamCount / tableCount);
        var entriesTable2 = Math.floor(teamCount / tableCount);
    } else {
        var entriesTable1 = teamCount / tableCount;
        var entriesTable2 = teamCount / tableCount;
    }

    for (var i = 1; i <= tableCount; i++) {
        var table = document.createElement("table");
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");

        table.className = "table" + i;

        var headerRow = thead.insertRow(0);
        var headerCellGroup = headerRow.insertCell(0);
        headerCellGroup.textContent = "Gruppe " + String.fromCharCode(64 + i);
        headerCellGroup.className = "headerCell";

        var headerCellSp = headerRow.insertCell(1);
        headerCellSp.textContent = "Sp";
        headerCellSp.className = "headerCell";

        var headerCellT = headerRow.insertCell(2);
        headerCellT.textContent = "T";
        headerCellT.className = "headerCell";

        var headerCellP = headerRow.insertCell(3);
        headerCellP.textContent = "P";
        headerCellP.className = "headerCell";

        if (i == 1) {
            for (var j = 1; j <= entriesTable1; j++) {
                var row = tbody.insertRow(j - 1);
                var cellName = row.insertCell(0);
                cellName.textContent = j;
                cellName.className = "tableCell";
                cellName.className += " nameCell" + j;

                var cellSp = row.insertCell(1);
                cellSp.textContent = 0;
                cellSp.className = "tableCell";
                cellSp.className += " sCell" + j;

                var cellT = row.insertCell(2);
                cellT.textContent = ":";
                cellT.className = "tableCell";
                cellT.className += " tCell" + j;

                var cellP = row.insertCell(3);
                cellP.textContent = 0;
                cellP.className = "tableCell";
                cellP.className += " pCell" + j;
            }
        } else if (i == 2) {
            for (var j = 1; j <= entriesTable2; j++) {
                var row = tbody.insertRow(j - 1);
                var cellName = row.insertCell(0);
                cellName.textContent = j;
                cellName.className = "tableCell";
                cellName.className += " nameCell" + j;

                var cellSp = row.insertCell(1);
                cellSp.textContent = 0;
                cellSp.className = "tableCell";
                cellSp.className += " sCell" + j;

                var cellT = row.insertCell(2);
                cellT.textContent = ":";
                cellT.className = "tableCell";
                cellT.className += " tCell" + j;

                var cellP = row.insertCell(3);
                cellP.textContent = 0;
                cellP.className = "tableCell";
                cellP.className += " pCell" + j;
            }
        }

        table.appendChild(thead);
        table.appendChild(tbody);
        tablesContainer.appendChild(table);
    }

    console.log("Initial data:", data);

    updateTables(data);
}

function updateData() {
    // Include the last data version in the request headers
    var headers = new Headers();
    headers.append("Last-Data-Update", data["LastUpdate"]);

    fetch("/update_data", {
        headers: headers,
    })
        .then((response) => response.json())
        .then((updatedData) => {
            console.log("Updated data:", updatedData);
            for (var key in data) {
                if (updatedData.hasOwnProperty(key)) {
                    data[key] = updatedData[key];
                }
            }
            // Wait 500ms before calling updateTables
            setTimeout(function () {
                updateTableSize();
            }, 500);
        })
        .catch((error) => console.error("Error fetching data:", error));
}

function updateTables(data) {
    var tableCount = 2;
    var teamCount = data.Teams.length;
    if (teamCount % 2 != 0) {
        var entriesTable1 = Math.ceil(teamCount / tableCount);
        var entriesTable2 = Math.floor(teamCount / tableCount);
    } else {
        var entriesTable1 = teamCount / tableCount;
        var entriesTable2 = teamCount / tableCount;
    }

    for (var x = 1; x < tableCount + 1; x++) {
        var tables = Array.from(
            document.querySelectorAll(`.table${x} tbody tr`)
        );
        // update team names

        console.log("table", x);

        var y = 1;
        if (x == 1) {
            var entriesPerTable = entriesTable1;
        } else if (x == 2) {
            var entriesPerTable = entriesTable2;
        }
        for (
            var i = x * entriesTable1 - entriesTable1;
            i < data.Teams.length && y < entriesPerTable + 1;
            i++
        ) {
            var team = data.Teams[i];
            var Sp = data.Spiele[i];
            var T = data.Tore[i];
            var T1 = T[0];
            var T2 = T[1];
            var P = Math.floor(Math.random() * 10) + 1;

            console.log("team", team, "Sp", Sp, "T", T, "P", P);

            tables.forEach(function (table) {
                var nameCell = table.getElementsByClassName("nameCell" + y)[0];
                if (nameCell) {
                    nameCell.textContent = team;
                }

                var sCell = table.getElementsByClassName("sCell" + y)[0];
                if (sCell) {
                    sCell.textContent = Sp;
                }

                var tCell = table.getElementsByClassName("tCell" + y)[0];
                if (tCell) {
                    tCell.textContent = `${T1} : ${T2}`;
                }

                var pCell = table.getElementsByClassName("pCell" + y)[0];
                if (pCell) {
                    pCell.textContent = P;
                }
            });
            y++;
        }
        var table = document.querySelector("#tablesContainer .table" + x);
        sortRowsByPoints(table);
    }
}

function updateTableSize() {
    // Delete both tables
    var table1 = document.getElementById("table1");
    var table2 = document.getElementById("table2");

    if (table1) {
        table1.remove();
    }

    if (table2) {
        table2.remove();
    }

    // Replace them with the generateTables function
    generateTables();
}

function sortRowsByPoints(table) {
    var tbody = table.querySelector("tbody");
    var rows = Array.from(tbody.querySelectorAll("tr"));

    rows.sort(function (a, b) {
        var aPCell = a.querySelector("[class*='pCell']");
        var bPCell = b.querySelector("[class*='pCell']");
        console.log("aPCell", aPCell, "bPCell", bPCell);
        var aP = aPCell ? parseInt(aPCell.textContent) : 0;
        var bP = bPCell ? parseInt(bPCell.textContent) : 0;
        console.log("aP", aP, "bP", bP);
        return bP - aP;
    });

    while (tbody.firstChild) {
        tbody.firstChild.remove();
    }

    for (var i = 0; i < rows.length; i++) {
        tbody.appendChild(rows[i]);
    }
}

// Function to handle button clicks and redirect
function redirectTo(path) {
    window.location.href = path;
}

document.getElementById("returnButton").addEventListener("click", function () {
    redirectTo("/");
});

// generate tables on page load
generateTables();

// call updateData() every 5 seconds
setInterval(updateData, 2000);
