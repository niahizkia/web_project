//------------------------------------------------------------------------------------
//--------------GET-VARIABLE-BY-ID----------------------------------------------------
//------------------------------------------------------------------------------------
var ID = function (elID) {
    return document.getElementById(elID);
  };
  
  var hide = function (id) {
    return id.classList.add("d-none");
  };
  
  var show = function (id) {
    return id.classList.remove("d-none");
  };


var formPreprocess  = ID("formPreprocess");
var formPreprocess  = ID("formPreprocess");

var btnPreprocess   = ID("btnPreprocess");


//------------------------------------------------------------------------------------
//-------------------T E S T I N G----------------------------------------------------
//------------------------------------------------------------------------------------
$(formTesting).submit(function (e) {
    e.preventDefault();
    show(emptyTest);
    hide(resTest);
    hide(resTestingReport);
    hide(btnTest);
  
    show(btnTestReset);
    show(spinnerTest);
  
    var formData = new FormData(this);
    var xhr = $.ajax({
      url: "/testing",
      type: "POST",
      cache: false,
      contentType: false,
      processData: false,
      data: formData,
      success: function (data) {
        obj = $.parseJSON(data);
  
        hide(spinnerTest);
        hide(emptyTest);
        show(resTest);
        $('#resultTestAcc').text(obj["result"]);
        $('#resultTestNum').text(obj["number"]);
        btnResTest.onclick = function () {
          var fileobj = JSON.parse(data);
          var fileloc = fileobj.file;
          show(resTestingReport);
          setupResDataTest(fileloc);
        };
  
      },
      error: function (xhr, ajaxOption, thrownError) {
        // eslint-disable-next-line no-undef
        Swal.fire({
          icon: "error",
          title: "Proses Dibatalkan",
          confirmButtonColor: "#577EF4",
        });
        location.reload();
      },
    });
  
    btnTestReset.onclick = function () {
      xhr.abort();
      $(formTesting)[0].reset();
      $(tbTest).dataTable().fnDestroy(); //reset data table
      hide(btnTestReset);
      hide(resTest);
      hide(resTestingReport);
      hide(spinnerTest);
      show(btnTest);
    };
  
  });

//------------------------------------------------------------------------------------
//-----------------FUCTION-HELPER----------------------------------------------------
//------------------------------------------------------------------------------------


function setupResDataTest() {
    var urlFile = '/static/file/export.xlsx'
    $('#tbTest').DataTable({
      "ajax": {
        "url": urlFile,
        "dataType": "json",
        "dataSrc": "data",
        "contentType": "application/json"
      },
      "columns": [
        {
          "data": "review"
        },
        {
          "data": "prediction"
        }
      ],
  
      "columnDefs": [{
          "className": "text-left",
          "targets": "_all"
        },
      ],
    });
  
  }
  