document.addEventListener("DOMContentLoaded", () => {
  const logo = document.querySelector(".sidebar-header .sidebar-logo.light-content");
  const title = document.querySelector(".sidebar-header .sidebar-title");
  const secondaryNav = document.querySelector("nav.quarto-secondary-nav");

  if (!logo || !title || !secondaryNav) return;

  const brand = document.createElement("div");
  brand.className = "ds-mobile-brand";

  const logoClone = logo.cloneNode(true);
  logoClone.className = "ds-mobile-brand-logo";

  const titleClone = title.cloneNode(true);
  titleClone.className = "ds-mobile-brand-title";

  brand.appendChild(logoClone);
  brand.appendChild(titleClone);

  secondaryNav.insertAdjacentElement("afterbegin", brand);
});