$(document).ready(function () {
    // Clear the output box
    function clearOutput() {
        $("#resultPositives").text("");
    }

    $("#clearBtn").click(clearOutput);

    // Fetch recommendations from API and show them to user
    $("#recommendBtn").click(function () {
        clearOutput();
        $("#spinner").show();

        const inputText = $("#inputText").val().trim();
        if (inputText.length === 0) {
            return;
        }

        $.get(
            `http://localhost:8000/positives/${inputText}`,
            function (data, status) {
                $("#spinner").hide();
                data.forEach((element) => {
                    $("#resultPositives").append(
                        `<li>${element.title} [${element.avg_rating.toFixed(
                            1,
                        )}, ${element.correlation_idx.toFixed(3)}]</li>`,
                    );
                });
            },
        ).fail(function (jqXHR, textStatus, errorThrown) {
            $("#spinner").hide();
            $("#resultPositives").append(
                `<p>${jqXHR.status} ${textStatus} ${errorThrown}</p>`,
            );
        });
    });
});
