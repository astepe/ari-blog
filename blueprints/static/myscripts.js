
function fadeOutEffect() {
  var fadeTarget = document.getElementsByClassName("fade");
  var fadeEffect = setInterval(function () {
    if (!fadeTarget.style.opacity) {
        fadeTarget.style.opacity = 1;
    }
    if (fadeTarget.style.opacity > 0) {
        fadeTarget.style.opacity -= 0.1;
    } else {
        clearInterval(fadeEffect);
    }
  }, 200);
}


function displayResults(results) {

  var sds_chart = document.getElementById('requested_sds_data');

  while (sds_chart.firstChild) {
    sds_chart.removeChild(sds_chart.firstChild);
  }

  sds_data_titles = {
        'manufacturer': 'Manufacturer',
        'product_name': 'Product Name',
        'flash_point': 'Flash Point',
        'specific_gravity': 'Specific Gravity',
        'nfpa_fire': 'NFPA Fire',
        'nfpa_health': 'NFPA Health',
        'nfpa_reactivity': 'NFPA Reactivity',
        'sara_311': 'SARA 311/312',
        'revision_date': 'Revision Date',
        'physical_state': 'Physical State',
        'cas_number': 'CAS # (if pure)'
    }

  for (var key in results) {
    var categoryOutputList = document.createElement('div');

    var categoryItem = document.createElement('div');
    var h3 = document.createElement('h3');
    var h3Text = document.createTextNode(sds_data_titles[key] + ":");
    categoryOutputList.className = "category_output_list_item";
    categoryItem.className = "category_item";

    h3.appendChild(h3Text);
    categoryItem.appendChild(h3);
    categoryOutputList.appendChild(categoryItem);

    categoryItem = document.createElement('div');
    var p = document.createElement('p');
    var pText = document.createTextNode(results[key]);
    p.id = key + "_text";
    categoryItem.className = "category_item";

    p.appendChild(pText);
    categoryItem.appendChild(p);
    categoryOutputList.appendChild(categoryItem);

    var copyButtonDiv = document.createElement('div')
    copyButtonDiv.className = "category_item";
    var copyButton = document.createElement('button');
    var copyButtonText = document.createTextNode('Copy to clipboard');
    var onclick = document.createAttribute("onclick");
    copyButton.className = "copy_button";
    copyButton.id = key + "_button";
    onclick.value = "copyFunction('"+ key +"');";
    copyButton.setAttributeNode(onclick);

    copyButton.append(copyButtonText);
    copyButtonDiv.appendChild(copyButton)
    categoryOutputList.appendChild(copyButtonDiv);

    sds_chart.appendChild(categoryOutputList);

  };
};

function copyFunction(category) {

  var copyText = document.getElementById(category + "_text");
  var temp = document.createElement('textarea');
  temp.value = copyText.innerHTML;
  temp.setAttribute('readonly', '');
  temp.style = {position: 'absolute', left: '-9999px'};
  document.body.appendChild(temp);
  temp.select();
  document.execCommand("copy");
  document.body.removeChild(temp);

  var copyButtons = document.getElementsByClassName("copy_button");
  for (i = 0; i < copyButtons.length; i++) {
    if(copyButtons[i].innerHTML === "Text Copied!"){
      copyButtons[i].innerHTML = "Copy to clipboard";
    };
  };
  var copyButton = document.getElementById(category + "_button");
  copyButton.innerHTML = "Text Copied!"

}

function selectAll() {
  var check_box_labels = document.getElementsByClassName("check_box_label");
  var check_boxes = document.getElementsByClassName("check_box");
  var select_all_box = document.getElementById("select_all");

  // check boxes
  for (i = 0; i < check_boxes.length; i++) {
    check_boxes[i].checked = select_all_box.checked;
  };
  // update css
  if (select_all_box.checked) {
    Array.from(check_box_labels).forEach((element)=>{
      if (!(element.classList.contains("check_box_label_clicked"))){
        element.classList.add("check_box_label_clicked")
      }
    });
  }
  else {
    Array.from(check_box_labels).forEach((element)=>{
      if (element.classList.contains("check_box_label_clicked")){
        element.classList.remove("check_box_label_clicked")
      }
    });
  }
};
