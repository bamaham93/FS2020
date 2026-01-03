// Lazy-load METARs for each aircraft card
document.addEventListener('DOMContentLoaded', function() {
	const metarDivs = document.querySelectorAll('[id^="metar-container-"]');
	metarDivs.forEach(function(div, idx) {
		const icao = div.getAttribute('data-icao');
		if (!icao) return;
		fetch(`/fs2020/api/metar/?icao=${icao}`)
			.then(resp => resp.json())
			.then(data => {
				if (data.error) {
					div.innerHTML = `<span class='text-danger'>${data.error}</span>`;
					return;
				}
				let parsed = '';
				if (data.temp_c !== null) parsed += `<span class='me-2'>Temp: ${data.temp_c}&deg;C</span>`;
				if (data.dew_c !== null) parsed += `<span class='me-2'>Dewpoint: ${data.dew_c}&deg;C</span>`;
				if (data.wind) parsed += `<span class='me-2'>Wind: ${data.wind}</span>`;
				if (data.wind_gust) parsed += `<span class='me-2'>${data.wind_gust}</span>`;
				if (data.visibility) parsed += `<span class='me-2'>Visibility: ${data.visibility}</span>`;
				if (data.sky) parsed += `<span class='me-2'>Sky: ${data.sky}</span>`;
				if (data.altimeter) parsed += `<span class='me-2'>Altimeter: ${data.altimeter}</span>`;
				if (data.remarks) {
					parsed += `<span class='me-2'>Remarks: ${data.remarks}</span>`;
					if (data.remarks_translated) parsed += `<br><span class='text-success'>${data.remarks_translated}</span>`;
				}
				let observed = data.observation_time ? `<div class='text-muted small'>Observed: ${data.observation_time}</div>` : '';
				div.innerHTML = `
				  <strong>METAR:</strong>
				  <span id='metar-raw-${idx}'>${data.raw_text}</span>
				  <span id='metar-parsed-${idx}' style='display:none;'>${parsed}</span>
				  <label class='switch ms-2 align-middle' style='vertical-align:middle;'>
					<input type='checkbox' onchange='toggleMetar(${idx})'>
					<span class='slider round'></span>
				  </label>
				  <span class='small ms-1'>Parsed</span>
				  ${observed}
				`;
			})
			.catch(err => {
				div.innerHTML = `<span class='text-danger'>Error loading METAR</span>`;
			});
	});
});
// Toggle METAR raw/parsed display
function toggleMetar(idx) {
	var raw = document.getElementById('metar-raw-' + idx);
	var parsed = document.getElementById('metar-parsed-' + idx);
	if (raw.style.display === 'none') {
		raw.style.display = '';
		parsed.style.display = 'none';
	} else {
		raw.style.display = 'none';
		parsed.style.display = '';
	}
}
