function validateForm() {
				var x = '';
				if(document.getElementById("droparea").textContent!="Drop file here"){
					x = document.getElementById("droparea").textContent;
				}
				else {
					x = document.getElementById("text_field_1").value;
				}
				var y = "test2.csv";

				var newArr = x.split("\\")
				var new_x = newArr[newArr.length-1]

				if (new_x == "") {
					alert("File name(s) must be filled out.")
					return false;
				}
				if (y == ""){
					y.value = "wide_export.csv"
				}
				if(new_x === y) {
					alert("File names must be different.")
					return false;
				}
				if(new_x.length < 4 || y.length < 4 || y.substring(y.length - 4, y.length) != ".csv") {
					alert("Uploaded file must be a csv.")
					return false;
				}
				if(!document.getElementById("front_option").checked && !document.getElementById("back_option").checked) {
					alert("Must select a naming option (front or back).")
					return false;
				}
			}

function displayQuestion(answer) {

	if (answer == "False") {

		document.getElementById('subject_id_column').style.display = "block";
		document.getElementById('timepoint_column').style.display = "block";

	} else if (answer == "True") {

		document.getElementById('subject_id_column').style.display = "none";
		document.getElementById('timepoint_column').style.display = "none";

	}

}