export default {
	getReadWidget:   () => '<ma-number-column field="::field" value="::entry.values[field.name()]"></ma-number-column>',
	getLinkWidget:   () => '<a ng-click="gotoDetail()">' + module.exports.getReadWidget() + '</a>',
	getFilterWidget: () => '<ma-input-field type="number" step="any" field="::field" value="values[field.name()]"></ma-input-field>',
	getWriteWidget:  () => '<div class="input-group"><span class="input-group-addon">{{ field.currency() }}</span><ma-input-field type="number" step="any" field="::field" value="entry.values[field.name()]"></ma-input-field></div>'
};
