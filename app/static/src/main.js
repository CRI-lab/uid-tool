document.addEventListener("DOMContentLoaded", function loadJavascript() {
  var expandedRow = [];
  var tableBody = document.querySelector(".data-table-body");

  tableBody.addEventListener("click", function rowClick(event) {
    if (event.target.id == "uid") {
      copyToClipboard(event.target.innerText);
      event.target.setAttribute("data-tip", "Copied!");
    } else if (event.target.parentNode.classList.contains("main-detail")) {
      var nextRow = event.target.parentNode.nextElementSibling;
      toggleRow(event.target.parentNode.id, nextRow);
    }
  });
  tableBody.addEventListener("mouseout", function hoverOffUid(event) {
    if (event.target.id == "uid") {
      event.target.setAttribute("data-tip", "Copy To Clipboard");
    }
  });

  function toggleRow(id, nextRow) {
    console.log(expandedRow);
    if (expandedRow.includes(id)) {
      expandedRow.splice(expandedRow.indexOf(id), 1);
      nextRow.style.display = "none";
    } else {
      expandedRow.push(id);
      nextRow.style.display = "";
    }
  }

  function copyToClipboard(text) {
    navigator.clipboard
      .writeText(text)
      .then(function success() {
        return "Copied to Clipboard";
      })
      .catch(function (err) {
        return "Unable to copy text: ", err;
      });
  }
});
