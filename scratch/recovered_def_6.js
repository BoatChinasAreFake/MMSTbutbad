Created At: 2026-05-28T05:26:20Z
Completed At: 2026-05-28T05:26:20Z
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":95,"LineContent":"    \u003cbutton onclick=\"selectAllProvincesOfSelectedCountry()\" style=\""}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":105,"LineContent":"    \"\u003eSelect Country\u003c/button\u003e"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":172,"LineContent":"        \u003cinput type=\"text\" id=\"countrySearch\" placeholder=\"Search countries...\" style=\"width: 100%; box-sizing: border-box; background: #222; border: 1px solid #444; color: white; padding: 5px; border-radius: 4px; font-size: 12px;\" oninput=\"filterCountries()\"\u003e"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":175,"LineContent":"    \u003cdiv id=\"countryList\" style=\"display: flex; flex-direction: column; gap: 3px; max-height: 250px; overflow-y: auto; border: 1px solid #333; padding: 4px; border-radius: 4px; background: #111; margin-bottom: 8px;\"\u003e"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":343,"LineContent":"function selectCountry(tag) {"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":352,"LineContent":"    // Highlight the selected country in the list"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":353,"LineContent":"    const items = document.querySelectorAll(\".country-item\");"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":366,"LineContent":"function updateCountryList() {"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":367,"LineContent":"    const list = document.getElementById(\"countryList\");"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sin
<truncated 3835 bytes>
ntry = ownership[key];"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":1117,"LineContent":"\t\tif (!clickedCountry) return;"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":1119,"LineContent":"\t\tconst name = prompt(\"Rename country:\", countries[clickedCountry].name);"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":1121,"LineContent":"\t\t\trenameCountry(clickedCountry, name);"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":1189,"LineContent":"                // Check if owned by a country"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":1336,"LineContent":"\t\t\t\t\t\tselectCountry(tag);"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":1628,"LineContent":"\tfunction computeSpineForComponent(component, countryColor){"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":1742,"LineContent":"\t\t\treturn ownership[key] === countryColor;"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":2036,"LineContent":"\t\tconst country = countries[o];"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":2037,"LineContent":"\t\tif (!country) continue;"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":2039,"LineContent":"\t\tlet text = country.name.toUpperCase();"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":2043,"LineContent":"\t\t\tconst provincesSet = country.provinces;"}
{"File":"c:\\Users\\Faaz\\Documents\\GitHub\\Mappa Mundi sine Tempore\\index.html","LineNumber":2262,"LineContent":"\t\t\t// Limit the maximum gap to a generous threshold, allowing short names to stretch and span across the country"}