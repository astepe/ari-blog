var SDSDataResult;

function requestSDSData(event) {
  var xhr = new XMLHttpRequest();
  var url = "{{url_for('projects.submit_sds')}}";
  var form = document.forms[0];

  formData = new FormData(form);

  xhr.open('POST', url, true);

  xhr.onload = function() {
    if(this.status == 200) {
      let workerId = JSON.parse(this.responseText).worker_id;
      longPollSDSDataResult(workerId);
      displayResults(SDSDataResult.data);

      let submit = document.getElementById("submit")
      window.scrollTo({
          top: submit.offsetTop + submit.offsetHeight,
          behavior: 'smooth'
        });
      var loader = document.getElementById('loader');
      loader.style.opacity = 0;
    }
  }

  xhr.send(formData);
}
function sleep(milliseconds) {
  let start = new Date().getTime();
  for (let i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}


function longPollSDSDataResult(workerId) {
  while (SDSDataResult === undefined) {
    requestSDSDataResult(workerId)
    console.log(SDSDataResult);
    sleep(1000)
  }
}

function requestSDSDataResult(workerId) {

  let resultUrl = "{{url_for('projects.celery_result')}}"+ '?worker_id=' + workerId
  let xhr = new XMLHttpRequest();

  xhr.open('GET', resultUrl, false);
  xhr.setRequestHeader("Content-Type", "application/json");

  xhr.onload = function() {
    console.log('hi');
    if(this.status === 200) {
      console.log(this.responseText);
      SDSDataResult = JSON.parse(this.responseText);
    }
  }
  xhr.send();
}
