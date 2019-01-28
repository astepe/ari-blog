
function highlightSelectedCheckBoxLabel(check_box) {

    if (!(check_box.classList.contains("check_box_label_clicked"))) {
      check_box.classList.add("check_box_label_clicked")
    }
    else {
      check_box.classList.remove("check_box_label_clicked")
    }
};

let check_boxes = document.getElementsByClassName("check_box_label");


Array.from(check_boxes).forEach((element)=>{
  element.addEventListener("click", ()=>highlightSelectedCheckBoxLabel(element))
})

console.log(check_boxes)
