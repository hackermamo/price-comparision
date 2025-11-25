async function loadPreloadedProducts() {
    const res = await fetch("/preload_csv_products");
    const data = await res.json();
    const container = document.getElementById("csv-products");
    container.innerHTML = "";
  
    for (const site in data) {
      const section = document.createElement("div");
      section.innerHTML = `<h3>${site.toUpperCase()}</h3>`;
      const grid = document.createElement("div");
      grid.style.display = "flex";
      grid.style.flexWrap = "wrap";
      grid.style.gap = "10px";
  
      data[site].forEach(product => {
        const card = document.createElement("div");
        card.style.border = "1px solid #ddd";
        card.style.padding = "10px";
        card.style.width = "200px";
        card.innerHTML = `
          <a href="${product.product_url}" target="_blank">
            <img src="${product.image_link}" alt="Product" style="width:100%">
          </a>
          <p><strong>Price:</strong> ${product.price}</p>
          <p><strong>Site:</strong> ${product.site_name}</p>
        `;
        grid.appendChild(card);
      });
  
      section.appendChild(grid);
      container.appendChild(section);
    }
  }
  
  window.onload = loadPreloadedProducts;
  