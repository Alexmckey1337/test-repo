'use strict';

export default function addQueryParam(url, filter) {
	let filterKeys = Object.keys(filter);
	if (filterKeys && filterKeys.length) {
		url += '?';
		filterKeys.forEach(function (key) {
			if (Array.isArray(filter[key])) {
				if (filter[key].length < 1) {
					return
				}
				let filterItemValues = Object.values(filter[key]);
				filterItemValues.forEach(value => {
					url += `${key}=${value}&`;
				})
			} else {
				url += `${key}=${filter[key]}&`;
			}
		})
	}

	return url;
}