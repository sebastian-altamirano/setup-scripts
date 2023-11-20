/**
 * @file Removes spaces from a given bar code and prints the result on the console.
 */

const barCode = prompt("Enter the bar code:") || "";
const parsedBarCode = barCode.split(" ").join("");
console.log(parsedBarCode);
