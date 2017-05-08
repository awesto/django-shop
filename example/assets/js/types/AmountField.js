import NumberField from "admin-config/lib/Field/NumberField";

class AmountField extends NumberField {
	constructor(name) {
		super(name);
		this._currency = '$';
		this._type = "amount";
		this._baseFormat = '0.00';
		this._format = this._currency + this._baseFormat;
	}

	currency(currency) {
		if (!arguments.length) return this._currency;
		this._currency = currency;
		this._format = currency + this._baseFormat;
		return this;
	}

}

export default AmountField;
