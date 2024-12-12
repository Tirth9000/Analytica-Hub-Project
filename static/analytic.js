document.getElementById("fileInput").addEventListener("change", function (event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();

    reader.onload = function (e) {
      const data = e.target.result;
      const workbook = XLSX.read(data, { type: "binary" });
      const firstSheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[firstSheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });

      // Render data in the table
      renderTable(jsonData);
    };

    reader.readAsBinaryString(file);
  }
});

function renderTable(data) {
  const tableHead = document.querySelector("#dataTable thead");
  const tableBody = document.querySelector("#dataTable tbody");

  // Clear previous content
  tableHead.innerHTML = "";
  tableBody.innerHTML = "";

  if (data.length) {
    // Create table headers
    const headers = data[0];
    const headerRow = document.createElement("tr");
    headers.forEach((header) => {
      const th = document.createElement("th");
      th.textContent = header;
      headerRow.appendChild(th);
    });
    tableHead.appendChild(headerRow);

    // Create table rows
    for (let i = 1; i < data.length; i++) {
      const row = document.createElement("tr");
      data[i].forEach((cell) => {
        const td = document.createElement("td");
        td.textContent = cell !== undefined ? cell : "";
        row.appendChild(td);
      });
      tableBody.appendChild(row);
    }
  }
}