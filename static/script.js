//theme switching functions, it stores the theme in local storage
//you can see this in dev tools, but it's disabled on school laptops
function calculate({ localStorageTheme, systemSettingDark }) {
    return localStorageTheme || (systemSettingDark.matches ? "dark" : "light");
}
  
function updateButton({ buttonEl, isDark }) {
    const newCta = isDark ? "Change to light theme" : "Change to dark theme";
    buttonEl.setAttribute("aria-label", newCta);
    buttonEl.innerText = newCta;
}
  
function updateTheme({ theme }) {
    document.documentElement.setAttribute("data-theme", theme);
}
  
const button = document.querySelector("[data-theme-toggle]");
const localStorageTheme = localStorage.getItem("theme");
const systemSettingDark = window.matchMedia("(prefers-color-scheme: dark)");
  
let currentThemeSetting = calculate({ localStorageTheme, systemSettingDark });
  
updateButton({ buttonEl: button, isDark: currentThemeSetting === "dark" });
updateTheme({ theme: currentThemeSetting });
  
button.addEventListener("click", () => {
    const newTheme = currentThemeSetting === "dark" ? "light" : "dark";
  
    localStorage.setItem("theme", newTheme);
    updateButton({ buttonEl: button, isDark: newTheme === "dark" });
    updateTheme({ theme: newTheme });
  
    currentThemeSetting = newTheme;
});
  
systemSettingDark.addEventListener("change", (event) => {
    if (!localStorage.getItem("theme")) {
      const newSystemTheme = event.matches ? "dark" : "light";
      updateTheme({ theme: newSystemTheme });
      updateButton({ buttonEl: button, isDark: newSystemTheme === "dark" });
      currentThemeSetting = newSystemTheme;
    }
});
let transactions;

document.addEventListener("DOMContentLoaded", () => {
    const username= document.getElementById("username").textContent;
    if (username) {
        fetch(`/api/graphs/${username}`)
            //.then statements are to make sure the code is executed in the right order 
            // BECAUSE the request takes a VARIABLE amount of time
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                //prints the user's data to console for debugging
                console.log(data);
                
                const oneMonthAgo = new Date();
                oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
                const table = document.getElementById("tableHead");

                const recentTransactions = data.filter(transaction => {
                    const transactionDate = new Date(transaction.timestamp);
                    return transactionDate >= oneMonthAgo;
                });

                let income = 0;
                let expenses = 0;
                let balance = 0;
                recentTransactions.forEach(transaction => {
                    const row = document.createElement("tr");

                    // Create cells for each data field
                    const descriptionCell = document.createElement("td");
                    descriptionCell.textContent = transaction.description || "Unknown";
                    row.appendChild(descriptionCell);

                    const amountCell = document.createElement("td");
                    amountCell.textContent = `$${transaction.amount.toFixed(2)}`;
                    amountCell.className = transaction.transaction_type === "Income" ? "income" : "expense";
                    row.appendChild(amountCell);

                    const typeCell = document.createElement("td");
                    typeCell.textContent = transaction.transaction_type;
                    row.appendChild(typeCell);

                    const timestampCell = document.createElement("td");
                    timestampCell.textContent = new Date(transaction.timestamp).toLocaleString();
                    row.appendChild(timestampCell);

                    // Append the row to the table
                    table.appendChild(row);
                });

                //filters transactions by type
                const incomeTransactions = data.filter(transaction => transaction.transaction_type === "Income");
                incomeTransactions.forEach(transaction =>{
                    income += transaction.amount;
                    balance += transaction.amount;
                })
                const expenseTransactions = data.filter(transaction => transaction.transaction_type === "Expense");
                expenseTransactions.forEach(transaction =>{
                    expenses += transaction.amount;
                    balance += transaction.amount;
                })
                let balanceElement = document.getElementById("balance");
                balanceElement.textContent = "$" + `${balance}`
                let incomeElement = document.getElementById("income");
                incomeElement.textContent = "$" + `${income}`
                let expenseElement = document.getElementById("expenses");
                expenseElement.textContent = "$" + `${Math.abs(expenses)}`
                transactions = Object.assign({}, incomeTransactions, expenseTransactions);;

                // data preparation for income chart, maps descriptions
                // and amounts from the database to the NOW local data
                const incomeLabels = incomeTransactions.map(t => t.description || "Unknown");
                const incomeData = incomeTransactions.map(t => t.amount);

                //creates a chart.js chart
                const incomeChart = document.getElementById("incomeChart");
                new Chart(incomeChart, {
                    type: "pie",
                    data: {
                        labels: incomeLabels,
                        datasets: [{
                            data: incomeData,
                        }]
                    },
                    options: {
                        plugins: {
                            title: {
                                display: true,
                                text: "Income Distribution"
                            }
                        }
                    }
                });

                // data preparation for expense chart, maps descriptions and amounts from the database to the NOW local data
                const expenseLabels = expenseTransactions.map(t => t.description || "Unknown");
                const expenseData = expenseTransactions.map(t => Math.abs(t.amount));

                //creates a chart.js chart
                const expenseChart = document.getElementById("expensesChart");
                new Chart(expenseChart, {
                    type: "pie",
                    data: {
                        labels: expenseLabels,
                        datasets: [{
                            data: expenseData,
                        }]
                    },
                    options: {
                        plugins: {
                            title: {
                                display: true,
                                text: "Expense Distribution"
                            }
                        }
                    }
                });
                

            
            })
            .catch(error => {
                console.error('Error:', error);
            });
    } else {
        console.error("Username is not provided.");
    }
});