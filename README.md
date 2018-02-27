Uses Google's QPX flight search API to send emails when cheap flights are found.

Notice: Google has announced that they are closing their QPX service on April 10th, 2018.

The QPX Express API can be found here:
https://developers.google.com/qpx-express/

In order to use this application, you will need an API key.
The keys are freely available at the time of writing.
https://developers.google.com/qpx-express/v1/prereqs

Usage:

Create a config txt file with the following parameters, or create a copy
based on sample_config.txt.
Any line beginning with # is considered a comment and not parsed.

The port names can be either city codes or airport codes.
You can find these codes on sites such as http://www.airportcodes.org/.

For further information about the formatting, see the documentation in search_flights().

Required fields:

    City/airport code(s) in format:
    DEPARTURE_PORT = CHI
    ARRIVAL_PORT = TYO

    Date in YYYY-MM-DD format:
    DEPARTURE_DATE = 2017-04-01

    Number of days from departure to return:
    TRIP_LENGTH = 90

Optional fields:

    Maximum cost (in whole USD) of flight:
    MAX_COST = 1200

    +- variance for departure date and trip length:
    VARY_BY_DAYS = 5

    Maximum flight duration allowed (in minutes):
    MAX_DURATION = 1200

    Maximum number of flights to show (will show cheapest first):
    MAX_FLIGHTS = 30

Then run the following command:
flight_check.search_flights(config_file, recipient, sender, key_path, pw_path)

with the following arguments:

    config_file: string, the path to a text file as described above.

    recipient: string, the email address to which to send the results.

    sender: string, the email address from which to send the results.
        This must be an address from which you can send emails.

    key_path: string, the system path address where the QPX Express API
        key can be found. The key must be in a text file by itself.

    pw_path: string, the system path address where the email account's
        password can be found. The password must be in a text file by itself.

This creates up to QUERY_LIMIT queries for the arrival and departure port(s) within the specified date
ranges. Queries can also be limited by cost or number of results to return.

Next, it sends these queries to the QPX server and collects the results,
then sorts the results by increasing cost. Flights that require airport transfers
are omitted from the results. If MAX_FLIGHTS is set in the config file,
the result set is cropped to the first MAX_FLIGHTS results.

From there, it formats the results into a more human-readable format, creates an email
with the results, and sends it using the provided addresses.

The program needs access to the email account's password in order to send emails from it,
so for security reasons, it's recommended to use a dedicated or throwaway account.