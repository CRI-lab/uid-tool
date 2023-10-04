document.addEventListener("DOMContentLoaded", function loadJavascript() {
  var expandedRow = [];
  var tableBody = document.querySelector(".data-table-body");

  if (tableBody != null) {
    tableBody.addEventListener("click", function rowClick(event) {
      if (event.target.id == "remove-button") {
        var row = event.target.parentNode.parentNode.parentNode;
        var nextRow = row.nextElementSibling;
        closeRow(row.id, nextRow);
        row.setAttribute("data-being-removed", "true");
      }
      if (event.target.id == "uid") {
        copyToClipboard(event.target.innerText);
        event.target.setAttribute("data-tip", "Copied!");
      } else if (
        event.target.parentNode.classList.contains("main-detail") &&
        !event.target.parentNode.hasAttribute("data-being-removed")
      ) {
        var nextRow = event.target.parentNode.nextElementSibling;
        toggleRow(event.target.parentNode.id, nextRow);
      }
    });
    tableBody.addEventListener("mouseout", function hoverOffUid(event) {
      if (event.target.id == "uid") {
        event.target.setAttribute("data-tip", "Copy To Clipboard");
      }
    });
  }

  // var multiselectElement = document.getElementById("projects");
  // multiselectElement.addEventListener("click", function toggle(event) {
  //   var option = event.target;
  //   if (option.tagName == "OPTION") {
  //     if (option.hasAttribute("selected")) {
  //       option.removeAttribute("selected");
  //     } else {
  //       option.setAttribute("selected", "true");
  //     }
  //   }
  // });

  function toggleRow(id, nextRow) {
    if (expandedRow.includes(id)) {
      expandedRow.splice(expandedRow.indexOf(id), 1);
      nextRow.style.display = "none";
    } else {
      expandedRow.push(id);
      nextRow.style.display = "";
    }
  }

  function closeRow(id, nextRow) {
    if (expandedRow.includes(id)) {
      expandedRow.splice(expandedRow.indexOf(id), 1);
      nextRow.style.display = "none";
    }
  }

  function openRow(id, nextRow) {
    if (!expandedRow.includes(id)) {
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
