function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    var content = document.querySelector(".content");
    var cardContainer = document.getElementById("card-container");
    var tableDiv = document.getElementById("table-div");
    var addDiv = document.getElementById("add-div");
    sidebar.classList.toggle("open");
    content.classList.toggle("shifted");


    if (sidebar.classList.contains("open")) {
        content.style.marginLeft = "225px";
        if (cardContainer) {
            cardContainer.style.marginLeft = "215px";
        }
        if (tableDiv) {
            tableDiv.style.marginLeft = "246px";
        }
        if (addDiv) {
            addDiv.style.marginLeft = "235px";
        }
    } else {
        content.style.marginLeft = "0";
        if (cardContainer) {
            cardContainer.style.marginLeft = "0";
        }
        if (tableDiv) {
            tableDiv.style.marginLeft = "3%";
        }
        if (addDiv) {
            addDiv.style.marginLeft = "3%";
        }
    }


}

function toggleDropdown() {
    var dropdownContent = document.querySelector(".dropdown-content",);
    dropdownContent.classList.toggle("active");
}

function toggleDrop() {
    var dropdownContent = document.querySelector(".dropdown-content-sidebar");
    dropdownContent.classList.toggle("active");
}
function updateTable() {
    var rowsPerPage = document.getElementById("rowsPerPage").value;
    var table = document.querySelector(".allTable");
    var rows = table.getElementsByTagName("tr");

    // Start from 1 to skip the header row
    for (var i = 1; i < rows.length; i++) {
        if (i <= rowsPerPage) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

// Initial call to set up the table based on the default selection
document.addEventListener("DOMContentLoaded", function() {
    updateTable();
});

function deleteItem(model, itemId) {
    fetch('/delete-item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ model: model, itemId: itemId })
    }).then((_res) => {
        window.location.reload(); // Reload to reflect changes
    });
}