let currentFilter = 'upcoming';   // Display upcoming events by default

$(document).ready(function() {
    const eventTable = $('#events-table');

    $('#upcoming_events').on('click', function() {
        currentFilter = 'upcoming';
        $('#upcoming_events').removeClass('btn-outline-primary').addClass('btn-primary');
        $('#past_events').removeClass('btn-primary').addClass('btn-outline-primary');
        loadEvents();
    });

    $('#past_events').on('click', function() {
        currentFilter = 'past';
        $('#past_events').removeClass('btn-outline-primary').addClass('btn-primary');
        $('#upcoming_events').removeClass('btn-primary').addClass('btn-outline-primary');
        loadEvents();
    });

    $('#search_input').on('input', function() {
        loadEvents();
    });

    function loadEvents() {
        const search = $('#search_input').val();
        $.ajax({
            url: `?filter=${currentFilter}&search=${encodeURIComponent(search)}`,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
            dataType: 'json',
            success: function(data) {
                eventTable.empty();
                if (data.events.length === 0) {
                    eventTable.append('<tr><td colspan="4" class="text-center">No events found</td></tr>');
                    return;
                }
                $.each(data.events, function(index, event) {
                    const dateFormatted = new Date(event.date).toLocaleDateString();
                    const row = `
                        <tr>
                            <td>${event.title}</td>
                            <td>${dateFormatted}</td>
                            <td>${event.registration_count}</td>
                            <td><a href="/event/${event.id}/" class="btn btn-sm btn-outline-primary">View</a></td>
                        </tr>
                    `;
                    eventTable.append(row);
                });
            }
        });
    }
});
