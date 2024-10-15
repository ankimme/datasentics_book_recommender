$(document).ready(function () {
    // Clear both output boxes
    function clearOutput() {
        $("#resultPositives").text("");
        $("#resultNegatives").text("");
    }

    $("#clearBtn").click(clearOutput);

    // Fetch recommendations from API and show both positive and negative recommendations to user
    $("#recommendBtn").click(function () {
        clearOutput();
        const inputText = $("#inputText").val().trim();
        if (inputText.length === 0) {
            return;
        }

        $.get(
            `http://localhost:8000/positives/${inputText}`,
            function (data, status) {
                data.forEach((element) => {
                    $("#resultPositives").append(
                        `<li>${element.name} [${element.rating.toFixed(
                            1,
                        )}]</li>`,
                    );
                });
            },
        );

        $.get(
            `http://localhost:8000/negatives/${inputText}`,
            function (data, status) {
                data.forEach((element) => {
                    $("#resultNegatives").append(
                        `<li>${element.name} [${element.rating.toFixed(
                            1,
                        )}]</li>`,
                    );
                });
            },
        );
    });
});
