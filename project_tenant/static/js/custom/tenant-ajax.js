// Function to handle the agents status on the click of agent-act button.
$('.agent-act').live("click", function () {
    var ag_id;
    var act;
    ag_id = $(this).attr("data-id");
    act = $(this).attr("data-act");
    var msg;
    if (act == "0") {
        msg = "Are you sure to retire this Agent?"
    }
    else {
        msg = "Are you sure to Activate this Agent?"
    }
    if (window.confirm(msg)) {
        $.get('/admin/agent_action/', { id: ag_id, is_active: act }, function (data) {
        });
        if (act == "0") {
            $("#td" + ag_id).html("Retired")
            $(this).attr("data-act", "1");
            $(this).val("Activate");
            $(this).removeClass("btn-danger").addClass("btn-success");
            $(this).parent().siblings('.allocation').html('');
        }
        else {
            $("#td" + ag_id).html("Active")
            $(this).attr("data-act", "0");
            $(this).val("Retire");
            $(this).removeClass("btn-success").addClass("btn-danger");
            $(this).parent().siblings('.allocation').html('<input type="button"' +
                ' class="agent-allocate btn-success btn-rounded"' +
                ' data-id="' + ag_id + '" value="Allocate">');
        }
    }
});

// Allocating property to agent if he is active
$('.agent-allocate').live("click", function () {
    var ag_id = $(this).attr("data-id");
    location.href = '/admin/allocate_clone/?agent=' + ag_id;
});


$(function () {
    $("select").select2();
});

// Searching in Agent request on search textbox
$('#search').keyup(function () {
    var query;
    query = $(this).val();
    $.get('/admin/agent_request_search/', { suggestion: query }, function (data) {
        $('#tbl_agents').html(data);
    });
});


// Searching in Agent request on search textbox
$('#search_agent').keyup(function () {
    var query;
    query = $(this).val();
    $.get('/admin/agent_active_search/', { suggestion: query }, function (data) {
        $('#tbl_agents').html(data);
    });
});

// Showing agent allocation details
$('.show_data_agent').click(function () {
    var id = $(this).attr('data-id');
    var hidden = $(this).attr('data-hidden');
    var act = $(this).attr('data-act');

    if (hidden == '1') {
        $(this).parent().siblings().children(
            '.show_data_agent').html('<i class="icon-angle-down"></i>');
        $(this).parent().siblings().children(
            '.show_data_agent').attr('data-hidden', '1');
        $(this).parent().parent().next().removeClass("hidden");
        $(this).html('<i class="icon-angle-up"></i>');
        $(this).attr('data-hidden', '0');
        $this = $(this)
        $.get('/admin/show_data_agent/', { id: id, act: act }, function (data) {
            $this.parent().parent().next().children().html(data);
        });
    }
    else if (hidden == '0') {
        $(this).parent().parent().next().addClass("hidden");
        $(this).html('<i class="icon-angle-down"></i>');
        $(this).attr('data-hidden', '1');
    }
})

// Enabling User to create clone 
// Showing user clone_div area to create clone
$("#create_clone").change(function () {
    if ($(this).attr("checked")) {
        $("#clone_div").removeClass("hidden");
    }
    else {
        $("#clone_div").addClass('hidden');
    }

});



$('.move_from').live('click', function () {
    // alert($('#move_from option:selected'))
    $('#move_from option:selected').remove().appendTo('#move_to');
    $('#move_to option').attr('selected', 'selected');

});

$('.move_to').live('click', function () {
    // alert($('#move_from option:selected'))
    $('#move_to option:selected').remove().appendTo('#move_from');
    $('#move_to option').attr('selected', 'selected');

});

$('.move_all_from').live('click', function () {
    // alert($('#move_from option:selected'))
    $('#move_from option').remove().appendTo('#move_to');
    $('#move_to option').attr('selected', 'selected');

});

$('.move_all_to').live('click', function () {
    // alert($('#move_from option:selected'))
    $('#move_to option').remove().appendTo('#move_from');
    $('#move_to option').attr('selected', 'selected');

});

function check_existance(){
    $('#move_to option').each(function(){
        $('#move_from option[value='+($(this).val())+']').remove();
    }); 
      
}

// Showing user clone_div area to create clone
$("#msp").change(function () {
    if ($(this).val() == "") {
        $("#property").addClass('hidden');
    }
    else {
        $("#property").removeClass("hidden");
        $.get('/admin/move_to_clone_list/', { msp: $(this).val() }, function (data) {
            $('#property').html(data);
            $('#to_clone').select2();
        });
    }


});

// Showing user clone_div area to create clone
$("#msp_create_clone").change(function () {
    if ($(this).val() == "") {
        $("#property").addClass('hidden');
    }
    else {
        $("#property").removeClass("hidden");
        
    }


});


// Showing user clones for selecting property
$("#to_clone").live('change', function () {

    $("#manage_by_property").removeAttr('checked')
    if ($(this).val() == "") {
        $("#clone_div").addClass("hidden");
    }
    else {
        $("#clone_div").removeClass("hidden");
        $("#property_list").addClass('hidden');
        $('#clone_list').removeClass('hidden');
        $.get('/admin/move_from_clone_list/', {
            msp: $('#msp').val(),
            cln: $('#to_clone').val()
        }, function (data) {
            $('#clone_list').html(data);
            $('#from_clone').select2();
        });
    }


});

// Showing user clones for selecting property
$("#from_clone").live('change', function () {
    if ($(this).val() == "") {
        $("#property_list").addClass("hidden");
    }
    else {
        $('#property_list').removeClass("hidden");
        $.get('/admin/show_properties/', {
            id: $('#from_clone').val(),
            is_master: false
        }, function (data) {
            $('#property_select').html(data);
            check_existance();
        });
    }


});

// Showing user properties area to create clone
$("#manage_by_property").change(function () {
    if ($(this).attr("checked")) {
        $("#clone_list").addClass('hidden');
        $('#property_list').removeClass("hidden");
        $.get('/admin/show_properties/', {
            id: $('#msp').val(),
            cln: $('#to_clone').val(),
            is_master: true
        }, function (data) {
            $('#property_select').html(data);
            check_existance();
        });
    }
    else {
        $("#property_list").addClass('hidden');
        $('#clone_list').removeClass('hidden');
        $.get('/admin/move_from_clone_list/', {
            msp: $('#msp').val(),
            cln: $('#to_clone').val()
        }, function (data) {
            $('#clone_list').html(data);
            $('#from_clone').select2();
        });
    }

});



// Creating the list of clones.
$('#clone_no').keyup(function () {
    var no = $(this).val();
    if (Number(no) > 50) {
        $('#clone_list').html("<strong> Can not create more than 50 clones</strong>");
    }
    else {
        $.get('/admin/master_clone_list/', { clone_no: no }, function (data) {
            $('#clone_list').html(data);
        });
    }
});


// Showing Admin clone list while allocating Agent to Property.
$("#msp_list").change(function () {

    if ($(this).val() == "Select item") {
        $("#property").addClass('hidden');
    }
    else {
        $("#property").removeClass("hidden");
        // if(){
        //     alert($(this).attr('data-unallocated'))}
        $.get('/admin/property_clone_list/', {
            msp: $(this).val(),
            unallocated: $(this).attr('data-unallocated')
        }, function (data) {
            $('#property').html(data);
            $('#cln_list').select2();
        });
    }

});




// Showing more textboxes when user clicks plus button
$("#add_address").click(function () {
    var num = $("#num").val();
    // var new_html = '<input type="text" required name="pr_address'+num+'"/><a class="icon-minus-sign remove_address" ></a>';
    var new_html = '<div class="input-append" style="display:flex;" >' +
        '<input class="span2" id="appendedInputButton" name="pr_address' +
        num + '" type="text"><button class="btn btn-theme remove_address"' +
        'id="add_address" type="button"><i class="icon-minus"></i></button></div>'
    var new_num = Number(num) + 1;
    $("#num").val(new_num);
    $("#addresses").append(new_html);
    $("#addresses").find('input').last().focus();
});

// Removing the textbox on click of minus button
$(".remove_address").live("click", function () {
    $(this).parent().remove();
    $(this).remove();

});



$('.decimal_input').live('keyup', function () {
    var $this = $(this);

    // Get the value.
    var input = $this.val();

    var input = input.replace(/[\D\s\._\-]+/g, "");
    // input = input ? parseInt( input, 10 ) : 0;

    $this.val(function () {
        return (input === 0) ? "" : input.toLocaleString("en-IND");
    });
});

$('.show_data').click(function () {
    var id = $(this).attr('data-id');
    var hidden = $(this).attr('data-hidden');
    var act = $(this).attr('data-act');

    if (hidden == '1') {
        $(this).parent().siblings().children(
            '.show_data').html('<i class="icon-angle-down"></i>');
        $(this).parent().siblings().children(
            '.show_data').attr('data-hidden', '1');
        $("#tr" + id).removeClass("hidden");
        $(this).html('<i class="icon-angle-up"></i>');
        $(this).attr('data-hidden', '0');
        $.get('/admin/show_data/', { id: id, act: act }, function (data) {
            $('#td' + id).html(data);
        });
    }
    else if (hidden == '0') {
        $("#tr" + id).addClass("hidden");
        $(this).html('<i class="icon-angle-down"></i>');
        $(this).attr('data-hidden', '1');
    }
})

$('.edit_property').live('click', function () {
    $('#myModal').css('display', 'block');
    $tr = $(this).parent().parent();
    $("#id").val($(this).attr('data-id'))
    $("#pr_address").val($tr.children('.pr_address').html())
    $("#pr_clone").val($tr.children('.pr_clone').html())
    $("#pr_status").val($tr.children('.pr_status').html())
    $("#pr_rent").val($tr.children('.pr_rent').html())
    $("#pr_deposite").val($tr.children('.pr_deposite').html())
    $("#pr_description").val($tr.children('.pr_description').html())
    // alert($tr.children('.pr_address').html())
    // $('#pr_address').val();
    $ref = $tr;
})

$('#save').click(function () {
    $.get('/admin/edit_property/', {
        id: $("#id").val(),
        rent: parseFloat($("#pr_rent").val()),
        deposite: parseFloat($("#pr_deposite").val()),
        description: $("#pr_description").val()
    }, function (data) {
        if (data == '1') {
            alert("Data updated Successfully")
            $tr.children('.pr_rent').html(parseFloat($("#pr_rent").val()).toFixed(2))
            $tr.children('.pr_deposite').html(parseFloat($("#pr_deposite").val()).toFixed(2))
            $tr.children('.pr_description').html($("#pr_description").val())
            $('#myModal').css('display', 'none')
        }
        else {

            alert("Data not updated Successfully")
        }
    });

});

$('.close').click(function () {
    $('#myModal').css('display', 'none')
});

$('#close').click(function () {
    $('#myModal').css('display', 'none')
});

$('.deallocate_clone').live('click', function () {
    $.get('/admin/deallocate_clone/', { id: $(this).attr('data-id') }, function (data) {
        if (data == '1') {
            alert('Property deallocated ');
            location.reload('/admin/view_master_property/');
        }
        else {
            alert('Error accured while deallocating Property.')
        }
    })
});
$('.delete_clone').live('click', function () {
    $.get('/admin/delete_clone/', { id: $(this).attr('data-cln'), msp: $(this).attr('data-msp') }, function (data) {
        if (data == '1') {
            alert('Clone deleted');
            location.reload('/admin/view_master_property/');
        }
        else {
            alert('Error accured while deleting Clone.')
        }
    })
});

$('.allocate_clone').live('click', function () {
    var msp = $(this).attr('data-msp');
    var cln = $(this).attr('data-id');
    location.href = '/admin/allocate_clone/?msp=' + msp + '&cln=' + cln;
});

$('.delete_master').live('click', function () {
    if (confirm('Are you sure to remove this master property?')) {
        var $this = $(this);
        $.get('/admin/delete_master_property/', { id: $(this).attr('data-id') }, function (data) {
            if (data == '1') {
                // location.reload('/admin/view_master_property/');
                $this.parent().parent().next().remove();
                $this.parent().parent().remove();
                alert('Property Sold and Removed from system ');
            }
            else {
                alert('Error accured while Deleting Property.')
            }
        })
    }
});




function manage_form() {
    $('#move_to option').attr('selected', 'selected')
    // alert('donr')

}






// function allocate_agent() {
//     // alert('before submitting form')
//     var cln = document.forms["agent_allocation"]["pr_msp"].innerText;
//     var msp = document.forms["agent_allocation"]["pr_msp_clone"].innerText;
//     var agent = document.forms["agent_allocation"]["agentx"].innerText;

//     return window.confirm('clone '+cln+' of Master Property '+
//         msp+' Will be alloacted to '+agent+' agent')
// }

// $('#btnsuccess').click(function () {
//     var agent, clone;
//     agent = $('#selectedagent').val();
//     clone = $('#cln_list').val();
//     csrf=$('[name="csrfmiddlewaretoken"]').val();
//         $.post('/admin/allocate_clone/', {csrfmiddlewaretoken:csrf, pr_msp_clone: clone, agentx: agent }, function (data) {
//         if (data) 
//         {
//         alert('Data Inserted Successfully');
//             location.reload();
//             $('#msp_list').get(0).selectedIndex = 0;
//             $('#selectedagent').get(0).selectedIndex = 0;

//         }
//         else {
//             alert('Error in Allocation process');

//         }
//     });
// });
// function mycall() 
// {
//    alert("aaya");
//    var num = $(this).attr("data-num");
//     $(this).prev('input').remove();
// }
