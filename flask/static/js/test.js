import { getUsefulContents } from "./functions.js";

function show(data)
{
    alert(data);
}
getUsefulContents('http://127.0.0.1:5000/user', 'POST', data => { show(data); });