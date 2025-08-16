/**
 * @file Removes spaces from a given bar code and shows the result in an alert.
 */

const barCode = prompt("Enter the bar code:") ?? "";
const parsedBarCode = barCode.split(" ").join("");
alert(parsedBarCode);
