/**
 * @file Fills out the Plus Pagos form using data from a file, but does not click on the pay button.
 */

// ------------------------------------------ JSDoc utils ------------------------------------------

/**
 * @template Type
 * @typedef {Type[keyof Type]} ValueOf
 */

// --------------------------------------- Type definitions ----------------------------------------

/**
 * @typedef {{
 *   CreditCard: "0",
 *   DebitCard: "1",
 *   Debin: "2",
 * }} PaymentMethod
 *
 * @typedef {{
 *   DNI: "dni",
 *   CI: "cedula",
 *   LC: "lc",
 *   LE: "le",
 * }} IdentityDocumentType
 *
 * @typedef {{
 *   owner: string,
 *   number: string,
 *   expirationDate: {
 *     month: number,
 *     year: number,
 *   },
 *   securityCode: string,
 * }} PaymentCard
 *
 * @typedef {{
 *   cuit: string,
 *   alias: string,
 * }} DebinAlias
 *
 * @typedef {{
 *   cuit: string,
 *   cbu: string,
 * }} DebinCbu
 *
 * @typedef {(DebinAlias | DebinCbu)} Debin
 *
 * @typedef {{
 *   paymentMethod: PaymentMethod["CreditCard"],
 *   creditCard: PaymentCard,
 *   debitCard?: PaymentCard,
 *   debin?: Debin,
 * }} PaymentInformationCreditCard
 *
 * @typedef {{
 *   paymentMethod: PaymentMethod["DebitCard"],
 *   creditCard?: PaymentCard,
 *   debitCard: PaymentCard,
 *   debin?: Debin,
 * }} PaymentInformationDebitCard
 *
 * @typedef {{
 *   paymentMethod: PaymentMethod["Debin"],
 *   creditCard?: PaymentCard,
 *   debitCard?: PaymentCard,
 *   debin: Debin,
 * }} PaymentInformationDebin
 *
 * @typedef {(
 *   | PaymentInformationCreditCard
 *   | PaymentInformationDebitCard
 *   | PaymentInformationDebin
 * )} PaymentInformation
 *
 * @typedef {{
 *   type: ValueOf<IdentityDocumentType>,
 *   number: string,
 * }} DocumentInformation
 *
 * @typedef {{
 *   paymentInformation: PaymentInformation,
 *   email: string,
 *   document: DocumentInformation,
 *   dateOfBirth: {
 *     year: number,
 *     month: number,
 *     day: number,
 *   },
 * }} FormValue
 */

// --------------------------------------------- Enums ---------------------------------------------

/** @type {PaymentMethod} */
const PaymentMethod = {
	CreditCard: "0",
	DebitCard: "1",
	Debin: "2",
};

/** @type {IdentityDocumentType} */
const IdentityDocumentType = {
	DNI: "dni",
	CI: "cedula",
	LC: "lc",
	LE: "le",
};

// ----------------------------------------- Custom errors -----------------------------------------

class FormValueValidationError extends Error {
	/**
	 * @param {string=} message
	 */
	constructor(message) {
		super(message);
		this.name = "FormValueValidationError";
	}
}

class UnallowedPaymentMethodError extends Error {
	/**
	 * @param {string=} message
	 */
	constructor(message) {
		super(message);
		this.name = "UnallowedPaymentMethodError";
	}
}

class InvalidCardNumberError extends Error {
	/**
	 * @param {string=} message
	 */
	constructor(message) {
		super(message);
		this.name = "InvalidCardNumberError";
	}
}

class UnknownError extends Error {
	/**
	 * @param {string=} message
	 */
	constructor(message) {
		super(message);
		this.name = "UnknownError";
	}
}

class ElementNotFoundError extends Error {
	/**
	 * @param {string=} message
	 */
	constructor(message) {
		super(message);
		this.name = "ElementNotFoundError";
	}
}

class MaxRetriesError extends Error {
	/**
	 * @param {string=} message
	 */
	constructor(message = "Max retries exceeded.") {
		super(message);
		this.name = "MaxRetriesError";
	}
}

// ----------------------------------------- General utils -----------------------------------------

/**
 * Returns the first element matched by `selectors`, but only if it is of the expected type.
 *
 * @template ElementType
 *
 * @param {string} selectors
 * @param {new () => ElementType} elementType Expected type for the matched element.
 *
 * @returns {ElementType}
 * @throws {ElementNotFoundError} If no element is found or it is not of the expected type.
 */
function getElementOrThrow(selectors, elementType) {
	const element = document.querySelector(selectors);
	if (element instanceof elementType) {
		return element;
	}

	if (element === null) {
		throw new ElementNotFoundError(`No element found for selector: "${selectors}".`);
	}

	throw new ElementNotFoundError(
		`An element was found for selector: "${selectors}", but it is not an instance of the expected \
type.`,
	);
}

/**
 * Changes the value of the given input and simulates events to trigger any validations the input
 * may have.
 *
 * @param {HTMLInputElement} inputEl
 * @param {string} newValue
 *
 * @returns {void}
 */
function changeTextInputValue(inputEl, newValue) {
	inputEl.value = newValue;
	inputEl.dispatchEvent(new Event("change", { bubbles: true }));
	inputEl.dispatchEvent(new FocusEvent("blur"));
}

/**
 * Changes the value of the given input character by character and simulates events to trigger any
 * validations the input may have.
 *
 * @param {HTMLInputElement} inputEl
 * @param {string} newValue
 *
 * @returns {void}
 */
function changeTextInputValueKeyByKey(inputEl, newValue) {
	for (let character of newValue) {
		inputEl.dispatchEvent(new KeyboardEvent("keydown", { bubbles: true, key: character }));
		inputEl.dispatchEvent(new KeyboardEvent("keypress", { bubbles: true, key: character }));
		inputEl.value += character;
		inputEl.dispatchEvent(new InputEvent("input", { bubbles: true, data: inputEl.value }));
		inputEl.dispatchEvent(new KeyboardEvent("keyup", { bubbles: true, key: character }));
	}

	inputEl.dispatchEvent(new Event("change", { bubbles: true }));
	inputEl.dispatchEvent(new FocusEvent("blur"));
}

/**
 * Changes the value of the given select and simulates events to trigger any validations the select
 * may have.
 *
 * @param {HTMLSelectElement} selectEl
 * @param {string} newValue
 *
 * @returns {void}
 */
function changeSelectValue(selectEl, newValue) {
	selectEl.value = newValue;
	selectEl.dispatchEvent(new InputEvent("input", { bubbles: true, data: newValue }));
	selectEl.dispatchEvent(new Event("change", { bubbles: true }));
	selectEl.dispatchEvent(new FocusEvent("blur"));
}

/**
 * Repeatedly executes a predicate until it evaluates to `true` or a maximum number of retries is
 * reached.
 *
 * If the maximum number of retries is reached the promise will reject with `MaxRetriesError`.
 *
 * @param {() => boolean} predicate
 * @param {number=} delayInMs The delay between each execution of `predicate`.
 * @param {number=} maxRetries
 *
 * @returns {Promise<void>}
 */
async function waitFor(predicate, delayInMs = 50, maxRetries = 5) {
	return new Promise((resolve, reject) => {
		let retries = 0;
		const interval = setInterval(() => {
			if (predicate() || retries > maxRetries) {
				clearInterval(interval);

				if (retries > maxRetries) {
					reject(new MaxRetriesError());
				} else {
					resolve();
				}
			}
			++retries;
		}, delayInMs);
	});
}

/**
 * @param {number} year
 * @param {number} month
 * @param {number} day
 *
 * @returns {boolean}
 */
function isValidDate(year, month, day) {
	const date = new Date(year, month - 1, day);
	return date instanceof Date && !isNaN(date.valueOf());
}

/**
 * @param {string} email
 *
 * @returns {boolean}
 */
function isValidEmail(email) {
	const EMAIL_REGEX = /^([a-z0-9_.+-]+)@([\da-z.-]+)\.([a-z.]{2,6})$/;
	return EMAIL_REGEX.test(email);
}

/**
 * Returns the day or month in the format expected by the application selects.
 *
 * @param {number} dayOrMonth
 *
 * @returns {string}
 */
function formatDayOrMonthForSelect(dayOrMonth) {
	return String(dayOrMonth).padStart(2, "0");
}

// ---------------------------------- Form value validation utils ----------------------------------

/**
 * @overload
 *
 * @param {PaymentInformation} paymentInformation
 * @param {"creditCard"} paymentInformationJsonKey
 *
 * @returns {PaymentCard}
 * @throws {FormValueValidationError}
 */
/**
 * @overload
 *
 * @param {PaymentInformation} paymentInformation
 * @param {"debitCard"} paymentInformationJsonKey
 *
 * @returns {PaymentCard}
 * @throws {FormValueValidationError}
 */
/**
 * @overload
 *
 * @param {PaymentInformation} paymentInformation
 * @param {"debin"} paymentInformationJsonKey
 *
 * @returns {Debin}
 * @throws {FormValueValidationError}
 */
/**
 * Given a payment information, returns the payment method information.
 *
 * @param {PaymentInformation} paymentInformation
 * @param {"creditCard" | "debitCard" | "debin"} paymentMethodInformationJsonKey
 *
 * @returns {(PaymentCard | Debin)}
 * @throws {FormValueValidationError} If payment information is not provided.
 */
function getPaymentMethodInformationOrThrow(paymentInformation, paymentMethodInformationJsonKey) {
	const paymentMethodInformation = paymentInformation[paymentMethodInformationJsonKey];
	if (!paymentMethodInformation) {
		throw new FormValueValidationError(
			`\`/paymentInformation/${paymentMethodInformationJsonKey}\` is not provided.`,
		);
	}

	return paymentMethodInformation;
}

/**
 * Validate that the payment card has a valid expiration date and is not expired.
 *
 * @param {PaymentCard} paymentCard
 * @param {"creditCard" | "debitCard" } paymentCardJsonKey
 *
 * @returns {void}
 * @throws {FormValueValidationError} If the payment card is expired or the expiration date is not
 * valid.
 */
function validatePaymentCard(paymentCard, paymentCardJsonKey) {
	const LAST_DAY_OF_THE_MONTH = 0;

	const expirationDate = paymentCard.expirationDate;
	if (!isValidDate(expirationDate.year, expirationDate.month, LAST_DAY_OF_THE_MONTH)) {
		throw new FormValueValidationError(
			`\`/paymentInformation/${paymentCardJsonKey}/expirationDate\` is not a valid date.`,
		);
	}

	const parsedCardExpirationDate = new Date(
		expirationDate.year,
		expirationDate.month - 1,
		LAST_DAY_OF_THE_MONTH,
	);
	if (new Date() > parsedCardExpirationDate) {
		throw new FormValueValidationError(
			`\`/paymentInformation/${paymentCardJsonKey}/expirationDate\` is expired.`,
		);
	}
}

/**
 * Validate that the debin information includes the alias or CBU.
 *
 * @param {Debin} debin
 *
 * @returns {void}
 * @throws {FormValueValidationError} If neither alias nor CBU is provided.
 */
function validateDebin(debin) {
	if (!("alias" in debin || "cbu" in debin)) {
		throw new FormValueValidationError(
			"`/paymentInformation/debin` requires `/alias` or `/cbu` to be defined, but neither is \
provided.",
		);
	}
}

/**
 * Validates that the payment method and payment method information are valid.
 *
 * @param {PaymentInformation} paymentInformation
 *
 * @returns {void}
 * @throws {FormValueValidationError} If the payment information is not provided or is invalid.
 */
function validatePaymentInformation(paymentInformation) {
	/** @type {"creditCard" | "debitCard" | "debin"} */
	let paymentMethodInformationJsonKey;
	switch (paymentInformation.paymentMethod) {
		case PaymentMethod.CreditCard: {
			paymentMethodInformationJsonKey = "creditCard";
			const creditCardInformation = getPaymentMethodInformationOrThrow(
				paymentInformation,
				paymentMethodInformationJsonKey,
			);
			validatePaymentCard(creditCardInformation, paymentMethodInformationJsonKey);
			break;
		}
		case PaymentMethod.DebitCard: {
			paymentMethodInformationJsonKey = "debitCard";
			const debitCardInformation = getPaymentMethodInformationOrThrow(
				paymentInformation,
				paymentMethodInformationJsonKey,
			);
			validatePaymentCard(debitCardInformation, paymentMethodInformationJsonKey);
			break;
		}
		case PaymentMethod.Debin: {
			paymentMethodInformationJsonKey = "debin";
			const debinInformation = getPaymentMethodInformationOrThrow(
				paymentInformation,
				paymentMethodInformationJsonKey,
			);
			validateDebin(debinInformation);
			break;
		}
		default:
			throw new FormValueValidationError(
				"`/paymentInformation/paymentMethod` is not a valid payment method.",
			);
	}
}

// ----------------------------------------- Snippet steps -----------------------------------------

/**
 * Reads the form value from a JSON file and returns its value.
 *
 * The promise can reject with:
 * - AbortError: If no file is selected.
 * - NotAllowedError: If the browser does not have permission to read the file.
 * - SyntaxError: If the selected file is not a valid JSON.
 *
 * @returns {Promise<FormValue>}
 */
async function readFormValueFromFile() {
	/** @type [FileSystemFileHandle] */
	// @ts-expect-error At the time of writing this, `showOpenFilePicker` is experimental and is not
	// included in the `Window` interface.
	const [fileHandle] = await window.showOpenFilePicker({
		excludeAcceptAllOption: true,
		multiple: false,
		types: [
			{
				accept: { "application/json": [".json"] },
				description: "Form value",
			},
		],
	});
	const fileData = await fileHandle.getFile();
	return JSON.parse(await fileData.text());
}

/**
 * @param {FormValue} formValue
 *
 * @returns {void}
 * @throws {FormValueValidationError} If the form value is not valid.
 */
function validateFormValue(formValue) {
	const dateOfBirth = formValue.dateOfBirth;
	if (!isValidDate(dateOfBirth.year, dateOfBirth.month, dateOfBirth.day)) {
		throw new FormValueValidationError("`/dateOfBirth` is not a valid date.");
	}

	if (!Object.values(IdentityDocumentType).includes(formValue.document.type)) {
		throw new FormValueValidationError("`/document/type` is not a valid document type.");
	}

	if (!isValidEmail(formValue.email)) {
		throw new FormValueValidationError("`/email` is not a valid email address.");
	}

	validatePaymentInformation(formValue.paymentInformation);
}

/**
 * @param {ValueOf<PaymentMethod>} paymentMethod
 *
 * @returns {void}
 * @throws {ElementNotFoundError} If the payment method dropdown is not found or is not of the
 * expected type.
 * @throws {UnallowedPaymentMethodError} If the selected payment method is not allowed.
 */
function choosePaymentMethod(paymentMethod) {
	const paymentMethodEl = getElementOrThrow("#TipoMedioPago", HTMLSelectElement);
	if (!Object.values(paymentMethodEl.options).some((option) => option.value === paymentMethod)) {
		throw new UnallowedPaymentMethodError(
			`The selected payment method is not allowed for the tax that you want to pay.`,
		);
	}

	changeSelectValue(paymentMethodEl, paymentMethod);
}

/**
 * Fills in the fields related to the payment card, which are:
 * - Card owner.
 * - Card number.
 * - Expiration date.
 * - Security code.
 *
 * The promise can reject with:
 * - ElementNotFoundError: If any of the inputs used to fill in the payment card information are not
 * found or are not of the expected type.
 * - InvalidCardNumberError: If the card number is invalid.
 * - MaxRetriesError: If the card number took too long to validate.
 *
 * @param {PaymentCard} paymentCard
 *
 * @returns {Promise<void>}
 */
async function fillPaymentCard(paymentCard) {
	const paymentCardOwner = getElementOrThrow("#inputTitular", HTMLInputElement);
	changeTextInputValue(paymentCardOwner, paymentCard.owner);

	const paymentCardNumberEl = getElementOrThrow("#NumeroTarjeta", HTMLInputElement);
	changeTextInputValueKeyByKey(paymentCardNumberEl, paymentCard.number);
	try {
		await waitFor(() => {
			// While typing the card number the web page performs an HTTP request to determine the value
			// of this input. We need to wait for the value to be set as it is necessary to validate the
			// form and enable the payment button.
			const paymentMethodIdEl = getElementOrThrow("#MedioPagoId", HTMLInputElement);
			return paymentMethodIdEl.value !== "";
		});
	} catch (error) {
		if (error instanceof MaxRetriesError) {
			throw new MaxRetriesError(
				"Max retries exceeded while waiting for the card number to be validated. Increase the \
maximum number of retries or the delay between retries and try again.",
			);
		}

		throw error;
	}
	if (paymentCardNumberEl.ariaInvalid === "true") {
		throw new InvalidCardNumberError("The card number is not valid.");
	}

	const paymentCardExpirationDateMonthEl = getElementOrThrow(
		"#mesVencimiento",
		HTMLSelectElement,
	);
	changeSelectValue(
		paymentCardExpirationDateMonthEl,
		formatDayOrMonthForSelect(paymentCard.expirationDate.month),
	);

	const paymentCardExpirationDateYearEl = getElementOrThrow("#anios", HTMLSelectElement);
	changeSelectValue(paymentCardExpirationDateYearEl, String(paymentCard.expirationDate.year));

	const paymentCardSecurityCodeEl = getElementOrThrow("#CodSeguridad", HTMLInputElement);
	changeTextInputValueKeyByKey(paymentCardSecurityCodeEl, paymentCard.securityCode);
}

/**
 * @param {Debin} debin
 *
 * @returns {void}
 * @throws {ElementNotFoundError} If any of the inputs used to fill in the debin information are not
 * found or are not of the expected type.
 */
function fillDebin(debin) {
	const cuitEl = getElementOrThrow("#Cuit", HTMLInputElement);
	changeTextInputValue(cuitEl, debin.cuit);

	if ("alias" in debin) {
		const chooseAliasEl = getElementOrThrow(
			"input[name='tipovalor'][value='Alias']",
			HTMLInputElement,
		);
		chooseAliasEl.click();
		const aliasEl = getElementOrThrow("#ValorAlias", HTMLInputElement);
		changeTextInputValue(aliasEl, debin.alias);
	} else {
		const chooseCbuEl = getElementOrThrow(
			"input[name='tipovalor'][value='CBU']",
			HTMLInputElement,
		);
		chooseCbuEl.click();
		const cbuEl = getElementOrThrow("#ValorCBU", HTMLInputElement);
		changeTextInputValue(cbuEl, debin.cbu);
	}
}

/**
 * Fills in the payment method and the payment method information.
 *
 * The promise can reject with:
 * - ElementNotFoundError: If any of the inputs used to fill in the payment information are not
 * found or are not of the expected type.
 * - UnallowedPaymentMethodError: If the selected payment method is not allowed.
 * - InvalidCardNumberError: If the card number is invalid.
 * - MaxRetriesError: If the card number took too long to validate.
 *
 * @param {PaymentInformation} paymentInformation
 *
 * @returns {Promise<void>}
 */
async function fillPaymentInformation(paymentInformation) {
	const paymentMethod = paymentInformation.paymentMethod;
	choosePaymentMethod(paymentMethod);

	switch (paymentMethod) {
		case PaymentMethod.CreditCard:
			await fillPaymentCard(paymentInformation.creditCard);
			break;
		case PaymentMethod.DebitCard:
			await fillPaymentCard(paymentInformation.debitCard);
			break;
		case PaymentMethod.Debin:
			fillDebin(paymentInformation.debin);
			break;
	}
}

/**
 * @param {string} email
 * @param {ValueOf<PaymentMethod>} paymentMethod
 *
 * @returns {void}
 * @throws {ElementNotFoundError} If the email input is not found or is not of the expected type.
 */
function fillEmail(email, paymentMethod) {
	const emailEl = getElementOrThrow(
		`#${paymentMethod === PaymentMethod.Debin ? "Email_Debin" : "Email"}`,
		HTMLInputElement,
	);
	changeTextInputValue(emailEl, email);
}

/**
 * @param {DocumentInformation} document
 *
 * @returns {void}
 * @throws {ElementNotFoundError} If any of the inputs used to fill in the document information are
 * not found or are not of the expected type.
 */
function fillDocument(document) {
	const documentTypeEl = getElementOrThrow("#select-documento", HTMLSelectElement);
	const documentNumberEl = getElementOrThrow("#numeroDocumento", HTMLInputElement);
	changeSelectValue(documentTypeEl, document.type);
	changeTextInputValue(documentNumberEl, document.number);
}

/**
 * @param {number} year
 * @param {number} month
 * @param {number} day
 *
 * @returns {void}
 * @throws {ElementNotFoundError} If any of the inputs used to fill in the date of birth are not
 * found or are not of the expected type.
 */
function fillDateOfBirth(year, month, day) {
	const yearElId = "#anioNacimiento";
	if (document.querySelector(yearElId) === null) return; // Date of birth is not always requested.

	const yearEl = getElementOrThrow(yearElId, HTMLSelectElement);
	const monthEl = getElementOrThrow("#mesNacimiento", HTMLSelectElement);
	const dayEl = getElementOrThrow("#diaNac", HTMLSelectElement);

	changeSelectValue(yearEl, String(year));
	changeSelectValue(monthEl, formatDayOrMonthForSelect(month));
	changeSelectValue(dayEl, formatDayOrMonthForSelect(day));
}

/**
 * @returns {void}
 * @throws {ElementNotFoundError} If the "accept terms and conditions" checkbox is not found or is
 * not of the expected type.
 */
function acceptTermsAndConditions() {
	const acceptTermsAndConditionsEl = getElementOrThrow(
		"#AceptTerminosyCondiciones",
		HTMLInputElement,
	);
	acceptTermsAndConditionsEl.click();
}

// -------------------------------------- Main program logic ---------------------------------------

/**
 * Fills out the Plus Pagos form using data from a file, but does not click on the pay button.
 *
 * The promise can reject with:
 * - AbortError: If no file is selected.
 * - NotAllowedError: If the browser does not have permission to read the file.
 * - SyntaxError: If the selected file is not a valid JSON.
 * - ElementNotFoundError: If any of the inputs used to fill out the form are not found or are not
 * of the expected type.
 * - UnallowedPaymentMethodError: If the selected payment method is not allowed.
 * - InvalidCardNumberError: If the card number is invalid.
 * - MaxRetriesError: If the card number took too long to validate.
 * - FormValueValidationError: If the file content is not valid.
 * - UnknownError: If the payment button is still disabled after filling out the form.
 *
 * @returns {Promise<void>}
 */
async function main() {
	try {
		const formValue = await readFormValueFromFile();
		validateFormValue(formValue);
		await fillPaymentInformation(formValue.paymentInformation);
		fillEmail(formValue.email, formValue.paymentInformation.paymentMethod);
		fillDocument(formValue.document);
		fillDateOfBirth(
			formValue.dateOfBirth.year,
			formValue.dateOfBirth.month,
			formValue.dateOfBirth.day,
		);
		acceptTermsAndConditions();

		const payButtonEl = getElementOrThrow("#confirmPago", HTMLButtonElement);
		if (payButtonEl.disabled) {
			throw new UnknownError(
				"The form has been filled up without errors but the payment button has not been enabled. \
The snippet is probably outdated or has not been thoroughly tested.",
			);
		}
	} catch (error) {
		alert(error);
		throw error;
	}
}

await main();
