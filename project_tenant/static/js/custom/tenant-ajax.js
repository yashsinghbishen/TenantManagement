$('.agent-act').click(function () {
    var ag_id;
    var act;
    ag_id = $(this).attr("data-id");
    act = $(this).attr("data-act");
    $.get('/admin/agent_action/', { id: ag_id, is_active: act }, function (data) {
    });
    if(act=="0")
    {
        $("#td"+ag_id).html("Retired")
        $(this).attr("data-act","1");
        $(this).val("Activate");
        $(this).removeClass("btn-danger").addClass("btn-success");
    }
    else
    {   
        $("#td"+ag_id).html("Active")
        $(this).attr("data-act","0");
        $(this).val("Retire");
        $(this).removeClass("btn-success").addClass("btn-danger");
    }
});


$('#search').keyup(function () {
    var query;
    query = $(this).val();
    $.get('/admin/agent_request_search/', { suggestion: query }, function (data) {
        $('#tbl_agents').html(data);
    });
});


