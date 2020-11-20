"use strict";
/*---------------------------------- GLOBALS ----------------------------------*/
var $top_list = ["Aatrox", "Akali", "Camille", "Chogath", "Darius", "DrMundo", "Fiora", "Gangplank",
             "Garen", "Gnar", "Gragas", "Hecarim", "Heimerdinger", "Illaoi", "Irelia", "Jax",
             "Jayce", "Kalista", "Karma", "Kayle", "Kennen", "Kled", "Lillia", "Lucian", "Malphite",
             "Maokai", "MonkeyKing", "Mordekaiser", "Nasus", "Neeko", "Ornn", "Pantheon", "Poppy",
             "Quinn", "Renekton", "Rengar", "Riven", "Rumble", "Ryze", "Sett", "Shen", "Singed",
             "Sion", "Swain", "Sylas", "TahmKench", "Teemo", "Trundle", "Tryndamere", "Urgot",
             "Vayne", "Vladimir", "Volibear", "Yasuo", "Yone", "Yorick"]
var $jg_list = ["Amumu", "Ekko", "Elise", "Evelynn", "Fiddlesticks", "Gragas", "Graves", "Hecarim", "Ivern",
                "JarvanIV", "Jax", "Karthus", "Kayn", "Khazix", "LeeSin", "MasterYi", "Nidalee", "Nocturne",
                "Nunu", "Olaf", "Rammus", "Rengar", "Sejuani", "Sett", "Shaco", "Shyvana", "Skarner",
                "Sylas", "Taliyah", "Trundle", "Udyr", "Volibear", "Warwick", "XinZhao", "Zac", "Lillia",
                "DrMundo", "Kindred", "RekSai", "Twitch", "Vi"]
var $mid_list = ["Ahri", "Akali", "Anivia", "Annie", "AurelionSol", "Cassiopeia", "Corki", "Diana", "Ekko",
                 "Fizz", "Galio", "Heimerdinger", "KogMaw", "Irelia", "Kassadin", "Katarina", "Leblanc",
                 "Lissandara", "Lucian", "Lux", "Malzahar", "Neeko", "Orianna", "Qiyana", "Ryze",
                 "Sylas", "Syndra", "TwistedFate", "Veigar", "Viktor", "Vladimir", "Xerath",
                 "Yasuo", "Zed", "Ziggs", "Zoe", "Azir", "Annie", "Karthus", "Malphite", "Gragas", "Renekton",
                 "Rumble", "Sett", "Talon", "Taliyah", "Velkoz", "Yone", "Zilean"]
var $bot_list = ["Aphelios", "Ashe", "Caitlyn", "Cassiopeia", "Draven", "Corki", "Ezreal", "Jhin", "Jinx",
                 "Kaisa", "Kalista", "KogMaw", "Lucian", "MissFortune", "Quinn", "Samira", "Senna", "Sivir",
                 "Tristana", "Twitch", "Syndra", "Heimerdinger", "Vayne", "Veiger", "Xayah", "Yasuo", "Ziggs",
                 "Varus", "Sona"]
var $supp_list = ["Alistar", "Bard", "Blitzcrank", "Brand", "Braum", "Galio", "Gragas", "Janna", "Karma", "Leona",
                  "Lulu", "Lux", "Maokai", "Morgana", "Nami", "Nautilus", "Pantheon", "Poppy", "Pyke", "Rakan",
                  "Senna", "Sett", "Shen", "Sona", "Soraka", "Swain", "TahmKench", "Taric", "Thresh", "Trundle",
                  "Veigar", "Velkoz", "Xerath", "Yuumi", "Zilean", "Zyra"]
var $click_count_array = [0, 0, 0, 0, 0];
var $click_count_role_red = [0, 0, 0, 0, 0];
var $click_count_role_blue = [0, 0, 0, 0, 0];
var $select_call_count = 0;
var $blue_pick_array = [1, 4, 5, 8, 9];
var $red_pick_array = [2, 3, 6, 7, 10];
var $ban_dict = {};
var $pick_dict = {};
var $ban_table_dict = {};
var $pick_table_dict = {};
var $curr_role_ban_table = "";
var $curr_role_pick_table = "";
var NUMBER_OF_REQUESTS = 0;
var RATE_LIMIT_IN_MS = 1000;
var NUMBER_OF_REQUESTS_ALLOWED = 2;
var BAN_STR = "ban";
var PICK_STR = "pick";
/*-----------------------------------------------------------------------------*/

/*
** Rate Limit Interval
*/
setInterval(function()
{
    NUMBER_OF_REQUESTS = 0;
}, RATE_LIMIT_IN_MS);

/*
** Ajax Event Listeners
*/
$(document).on({
    ajaxStart: function()
    {
        var $table = $.getPickTableElement();
        $table.empty();
        $table.append($('<div/>').addClass("loading"));
        $table = null;
    }
});

$(function()
{
    var side = $.urlSide();

    //TODO - https://stackoverflow.com/questions/30793066/how-to-avoid-memory-leaks-from-jquery
    //TODO - event delegation

    /*
    ** Filter Table - Search
    */
    $("#filtered-search").on("keyup", function()
    {
        $.resetFilterClickCount($click_count_array);
        var $input = $(this).val();
        // Reset Table back to previous state
        if (!($input))
        {
            $.resetDraftTable();
        }
        else
        {
            var $draft_table = $("#draft-table td:visible");
            $draft_table.filter(function()
            {
                var $champ_str = $(this).find("img").attr('src').split('/')[4].replace(".png", "");
                $(this).toggle($champ_str.indexOf($input) > -1);
            });
            $draft_table = null;
        }
        return;
    });

    /*
    ** Filter Table - Top Lane Button
    */
    $("#filtered-top").on('click', function(e)
    {
        e.preventDefault();
        $.resetFilterClickCount($click_count_array, 0);
        $.resetDraftTable();
        $click_count_array[0]++;
        // Toggle
        if (($click_count_array[0] % 2) == 1)
        {
            var $draft_table_hidden = $("#draft-table td:hidden");
            var $draft_table = $("#draft-table td");
            $draft_table_hidden.toggle();
            $draft_table.each(function()
            {
                var $champ = $(this).find("img").attr("src").split("/")[4].replace(".png", "");
                if ($.isInDictionary($champ, $ban_dict) || $.isInDictionary($champ, $pick_dict))
                {
                    $(this).toggle();
                }
                if ($top_list.indexOf($champ) == -1 && $(this).is(":visible"))
                {
                    $(this).toggle();
                }
            });
            $draft_table_hidden = null;
            $draft_table = null;
        }
        // Untoggle
        else{$.resetDraftTable();}
        return;
    });

    /*
    ** Filter Table - Jungle Button
    */
    $("#filtered-jg").on('click', function(e)
    {
        e.preventDefault();
        $.resetFilterClickCount($click_count_array, 1);
        $.resetDraftTable();
        $click_count_array[1]++;
        // Toggle
        if (($click_count_array[1] % 2) == 1)
        {
            var $draft_table_hidden = $("#draft-table td:hidden");
            var $draft_table = $("#draft-table td");
            $draft_table_hidden.toggle();
            $draft_table.each(function()
            {
                var $champ = $(this).find("img").attr("src").split("/")[4].replace(".png", "");
                if ($.isInDictionary($champ, $ban_dict) || $.isInDictionary($champ, $pick_dict))
                {
                    $(this).toggle();
                }
                if ($jg_list.indexOf($champ) == -1 && $(this).is(":visible"))
                {
                    $(this).toggle();
                }
            });
            $draft_table_hidden = null;
            $draft_table = null;
        }
        // Untoggle
        else{$.resetDraftTable();}
        return;
    });

    /*
    ** Filter Table - Middle Button
    */
    $("#filtered-mid").on('click', function(e)
    {
        e.preventDefault();
        $.resetFilterClickCount($click_count_array, 2);
        $.resetDraftTable();
        $click_count_array[2]++;
        // Toggle
        if (($click_count_array[2] % 2) == 1)
        {
            var $draft_table_hidden = $("#draft-table td:hidden");
            var $draft_table = $("#draft-table td");
            $draft_table_hidden.toggle();
            $draft_table.each(function()
            {
                var $champ = $(this).find("img").attr("src").split("/")[4].replace(".png", "");
                if ($.isInDictionary($champ, $ban_dict) || $.isInDictionary($champ, $pick_dict))
                {
                    $(this).toggle();
                }
                if ($mid_list.indexOf($champ) == -1 && $(this).is(":visible"))
                {
                    $(this).toggle();
                }
            });
            $draft_table_hidden = null;
            $draft_table = null;
        }
        // Untoggle
        else{$.resetDraftTable();}
        return;
    });

    /*
    ** Filter Table - Bottom Button
    */
    $("#filtered-bot").on('click', function(e)
    {
        e.preventDefault();
        $.resetFilterClickCount($click_count_array, 3);
        $.resetDraftTable();
        $click_count_array[3]++;
        if (($click_count_array[3] % 2) == 1)
        {
            var $draft_table_hidden = $("#draft-table td:hidden");
            var $draft_table = $("#draft-table td");
            $draft_table_hidden.toggle();
            $draft_table.each(function()
            {
                var $champ = $(this).find("img").attr("src").split("/")[4].replace(".png", "");
                if ($.isInDictionary($champ, $ban_dict) || $.isInDictionary($champ, $pick_dict))
                {
                    $(this).toggle();
                }
                if ($bot_list.indexOf($champ) == -1 && $(this).is(":visible"))
                {
                    $(this).toggle();
                }
            });
            $draft_table_hidden = null;
            $draft_table = null;
        }
        // Untoggle
        else{$.resetDraftTable();}
        return;
    });

    /*
    ** Filter Table - Support Button
    */
    $("#filtered-utility").on('click', function(e)
    {
        e.preventDefault();
        $.resetFilterClickCount($click_count_array, 4);
        $.resetDraftTable();
        $click_count_array[4]++;
        // Toggle
        if (($click_count_array[4] % 2) == 1)
        {
            var $draft_table_hidden = $("#draft-table td:hidden");
            var $draft_table = $("#draft-table td");
            $draft_table_hidden.toggle();
            $draft_table.each(function()
            {
                var $champ = $(this).find("img").attr("src").split("/")[4].replace(".png", "");
                if ($.isInDictionary($champ, $ban_dict) || $.isInDictionary($champ, $pick_dict))
                {
                    $(this).toggle();
                }
                if ($supp_list.indexOf($champ) == -1 && $(this).is(":visible"))
                {
                    $(this).toggle();
                }
            });
            $draft_table_hidden = null;
            $draft_table = null;
        }
        // Untoggle
        else{$.resetDraftTable();}
        return;
    });

    /*
    ** Ban Table Options - Filter By Role (Top)
    */
    $("#ban-top-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        if (!($curr_role_ban_table))
        {
            $.filterRole(BAN_STR, "top");
        }
        else
        {
            $.resetTable($ban_table_dict, BAN_STR);
            if ($curr_role_ban_table != "top")
            {
                $.filterRole(BAN_STR, "top");
            }
        }
        $curr_role_ban_table = $.switchCurrRole($curr_role_ban_table, "top");
        return;
    });

    /*
    ** Ban Table Options - Filter By Role (Jungle)
    */
    $("#ban-jg-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        if (!($curr_role_ban_table))
        {
            $.filterRole(BAN_STR, "jungle");
        }
        else
        {
            $.resetTable($ban_table_dict, BAN_STR);
            if ($curr_role_ban_table != "jungle")
            {
                $.filterRole(BAN_STR, "jungle");
            }
        }
        $curr_role_ban_table = $.switchCurrRole($curr_role_ban_table, "jungle");
        return;
    });

    /*
    ** Ban Table Options - Filter By Role (Middle)
    */
    $("#ban-mid-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        if (!($curr_role_ban_table))
        {
            $.filterRole(BAN_STR, "middle");
        }
        else
        {
            $.resetTable($ban_table_dict, BAN_STR);
            if ($curr_role_ban_table != "middle")
            {
                $.filterRole(BAN_STR, "middle");
            }
        }
        $curr_role_ban_table = $.switchCurrRole($curr_role_ban_table, "middle");
        return;
    });

    /*
    ** Ban Table Options - Filter By Role (Bottom)
    */
    $("#ban-bot-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        // Coming from No Filter - No Need to Reset Table
        if (!($curr_role_ban_table))
        {
            $.filterRole(BAN_STR, "bottom");
        }
        else
        {
            $.resetTable($ban_table_dict, BAN_STR);
            if ($curr_role_ban_table != "bottom")
            {
                $.filterRole(BAN_STR, "bottom");
            }
        }
        $curr_role_ban_table = $.switchCurrRole($curr_role_ban_table, "bottom");
        return;
    });

    /*
    ** Ban Table Options - Filter By Role (Support)
    */
    $("#ban-supp-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        if (!($curr_role_ban_table))
        {
            $.filterRole(BAN_STR, "utility");
        }
        else
        {
            $.resetTable($ban_table_dict, BAN_STR);
            if ($curr_role_ban_table != "utility")
            {
                $.filterRole(BAN_STR, "utility");
            }
        }
        $curr_role_ban_table = $.switchCurrRole($curr_role_ban_table, "utility");
        return;
    });

    /*
    ** Pick Table Options - Filter By Role (Top)
    */
    $("#pick-top-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        if (!($curr_role_pick_table))
        {
            $.filterRole(PICK_STR, "top");
        }
        else
        {
            $.resetTable($pick_table_dict, PICK_STR);
            if ($curr_role_pick_table != "top")
            {
                $.filterRole(PICK_STR, "top");
            }
        }
        $curr_role_pick_table = $.switchCurrRole($curr_role_pick_table, "top");
        return;
    });

    /*
    ** Pick Table Options - Filter By Role (Jungle)
    */
    $("#pick-jg-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        if (!($curr_role_pick_table))
        {
            $.filterRole(PICK_STR, "jungle");
        }
        else
        {
            $.resetTable($pick_table_dict, PICK_STR);
            if ($curr_role_pick_table != "jungle")
            {
                $.filterRole(PICK_STR, "jungle");
            }
        }
        $curr_role_pick_table = $.switchCurrRole($curr_role_pick_table, "jungle");
        return;
    });

    /*
    ** Pick Table Options - Filter By Role (Middle)
    */
    $("#pick-mid-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        if (!($curr_role_pick_table))
        {
            $.filterRole(PICK_STR, "middle");
        }
        else
        {
            $.resetTable($pick_table_dict, PICK_STR);
            if ($curr_role_pick_table != "middle")
            {
                $.filterRole(PICK_STR, "middle");
            }
        }
        $curr_role_pick_table = $.switchCurrRole($curr_role_pick_table, "middle");
        return;
    });

    /*
    ** Pick Table Options - Filter By Role (Bottom)
    */
    $("#pick-bot-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        if (!($curr_role_pick_table))
        {
            $.filterRole(PICK_STR, "bottom");
        }
        else
        {
            $.resetTable($pick_table_dict, PICK_STR);
            if ($curr_role_pick_table != "bottom")
            {
                $.filterRole(PICK_STR, "bottom");
            }
        }
        $curr_role_pick_table = $.switchCurrRole($curr_role_pick_table, "bottom");
        return;
    });

    /*
    ** Pick Table Options - Filter By Role (Support)
    */
    $("#pick-supp-filter").on('click', function(e)
    {
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        if (!($curr_role_pick_table))
        {
            $.filterRole(PICK_STR, "utility");
        }
        else
        {
            $.resetTable($pick_table_dict, PICK_STR);
            if ($curr_role_pick_table != "utility")
            {
                $.filterRole(PICK_STR, "utility");
            }
        }
        $curr_role_pick_table = $.switchCurrRole($curr_role_pick_table, "utility");
        return;
    });

    /*
    ** Ban Table Options - Filter By Rank
    */
    $("#ban-dropdown-rank span").on('click', function(e)
    {
        e.preventDefault();
        var $rank = $(this).text();
        $(this).parent().parent().children("span").text($rank);
        $(this).parent().css("display", "none");
        $.ajaxWrapper("GET", BAN_STR);
        $rank = null;
        return;
    });

    /*
    ** Ban Table Options - Filter By Rank (Hover)
    */
    $("#ban-dropdown-rank-meta").hover(
    function(e)
    {
        e.preventDefault();
        $(this).children("#ban-dropdown-rank").css("display", "block");
        return;
    },
    function()
    {
        $(this).children("#ban-dropdown-rank").css("display", "none");
        return;
    });

    /*
    ** Ban Table Options - Filter By Patch
    */
    $("#ban-dropdown-patch span").on('click', function(e)
    {
        e.preventDefault();
        var $patch = $(this).text();
        $(this).parent().parent().children("span").text($patch);
        $(this).parent().css("display", "none");
        $.ajaxWrapper("GET", BAN_STR)
        $patch = null;
        return;
    });

    /*
    ** Ban Table Options - Filter By Patch (Hover)
    */
    $("#ban-dropdown-patch-meta").hover(
    function(e)
    {
        e.preventDefault();
        $(this).children("#ban-dropdown-patch").css("display", "block");
        return;
    },
    function()
    {
        $(this).children("#ban-dropdown-patch").css("display", "none");
        return;
    });

    /*
    ** Pick Table Options - Filter By Rank
    */
    $("#pick-dropdown-rank span").on('click', function(e)
    {
        e.preventDefault();
        var $rank = $(this).text();
        $(this).parent().parent().children("span").text($rank);
        $(this).parent().css("display", "none");
        $rank = null;
        return;
    });

    /*
    ** Pick Table Options - Filter By Rank (Hover)
    */
    $("#pick-dropdown-rank-meta").hover(
    function(e)
    {
        e.preventDefault();
        $(this).children("#pick-dropdown-rank").css("display", "block");
        return;
    },
    function()
    {
        $(this).children("#pick-dropdown-rank").css("display", "none");
        return;
    });

    /*
    ** Pick Table Options - Filter By Patch
    */
    $("#pick-dropdown-patch span").on('click', function(e)
    {
        e.preventDefault();
        var $rank = $(this).text();
        $(this).parent().parent().children("span").text($rank);
        $(this).parent().css("display", "none");
        $rank = null;
        return;
    });

    /*
    ** Pick Table Options - Filter By Rank (Hover)
    */
    $("#pick-dropdown-patch-meta").hover(
    function(e)
    {
        e.preventDefault();
        $(this).children("#pick-dropdown-patch").css("display", "block");
        return;
    },
    function()
    {
        $(this).children("#pick-dropdown-patch").css("display", "none");
        return;
    });

    /*
    ** Pick Table Search Button
    */
    $("#" + side + "-query").on('click', function(e)
    {
        e.preventDefault();
        $.ajaxWrapper("GET", PICK_STR);
        return;
    });

    /*
    ** Ban Table - Display By Rank
    */
    $("#ban-by-rank").on('click', function(e)
    {
        var $dict_by_rank = {};
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        $dict_by_rank = $.sortByRank($ban_table_dict, $curr_role_ban_table);
        $.clearTable(BAN_STR);
        $.makeTable($dict_by_rank, BAN_STR);
        $dict_by_rank = null;
        return;
    });

    /*
    ** Ban Table - Display By Role
    */
    $("#ban-by-role").on('click', function(e)
    {
        var $dict_by_role = {};
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        $dict_by_role = $.sortByRole($ban_table_dict, $curr_role_ban_table);
        $.clearTable(BAN_STR);
        $.makeTable($dict_by_role, BAN_STR);
        $dict_by_role = null;
        return;
    });

    /*
    ** Ban Table - Display By Champion Name
    */
    $("#ban-by-champ").on('click', function(e)
    {
        var $dict_by_champ = {};
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        $dict_by_champ = $.sortByChamp($ban_table_dict, $curr_role_ban_table);
        $.clearTable(BAN_STR);
        $.makeTable($dict_by_champ, BAN_STR);
        $dict_by_champ = null;
        return;
    });

    /*
    ** Ban Table - Display By Win Rate
    */
    $("#ban-by-win").on('click', function(e)
    {
        var $dict_by_wins = {};
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        $dict_by_wins = $.sortByWinRate($ban_table_dict, $curr_role_ban_table);
        $.clearTable(BAN_STR);
        $.makeTable($dict_by_wins, BAN_STR);
        $dict_by_wins = null;
        return;
    });
    /*
    ** Ban Table - Display By Ban Rate
    */
    $("#ban-by-ban").on('click', function(e)
    {
        var $dict_by_bans = {};
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        $dict_by_bans = $.sortByBanRate($ban_table_dict, $curr_role_ban_table);
        $.clearTable(BAN_STR);
        $.makeTable($dict_by_bans, BAN_STR);
        $dict_by_bans = null;
        return;
    });

    /*
    ** Ban Table - Display By Pick Rate
    */
    $("#ban-by-pick").on('click', function(e)
    {
        var $dict_by_picks = {};
        e.preventDefault();
        $.loadTableDict($ban_table_dict, BAN_STR);
        $dict_by_picks = $.sortByPickRate($ban_table_dict, $curr_role_ban_table);
        $.clearTable(BAN_STR);
        $.makeTable($dict_by_picks, BAN_STR);
        $dict_by_picks = null;
        return;
    });

    /*
    ** Pick Table - Display By Rank
    */
    $("#pick-by-rank").on('click', function(e)
    {
        var $dict_by_rank = {};
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        $dict_by_rank = $.sortByRank($pick_table_dict, $curr_role_pick_table);
        $.clearTable(PICK_STR);
        $.makeTable($dict_by_rank, PICK_STR);
        $dict_by_rank = null;
        return;
    });

    /*
    ** Pick Table - Display By Role
    */
    $("#pick-by-role").on('click', function(e)
    {
        var $dict_by_role = {};
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        $dict_by_role = $.sortByRole($pick_table_dict, $curr_role_pick_table);
        $.clearTable(PICK_STR);
        $.makeTable($dict_by_role, PICK_STR);
        $dict_by_role = null;
        return;
    });

    /*
    ** Pick Table - Display By Champion Name
    */
    $("#pick-by-champ").on('click', function(e)
    {
        var $dict_by_champ = {};
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        $dict_by_champ = $.sortByChamp($pick_table_dict, $curr_role_pick_table);
        $.clearTable(PICK_STR);
        $.makeTable($dict_by_champ, PICK_STR);
        $dict_by_champ = null;
        return;
    });

    /*
    ** Pick Table - Display By Winrate
    */
    $("#pick-by-win").on('click', function(e)
    {
        var $dict_by_wins = {};
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        $dict_by_wins = $.sortByWinRate($pick_table_dict, $curr_role_pick_table);
        $.clearTable(PICK_STR);
        $.makeTable($dict_by_wins, PICK_STR);
        $dict_by_wins = null;
        return;
    });

    /*
    ** Pick Table - Display By Total Wins
    */
    $("#pick-by-ban").on('click', function(e)
    {
        var $dict_by_bans = {};
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        $dict_by_bans = $.sortByBanRate($pick_table_dict, $curr_role_pick_table);
        $.clearTable(PICK_STR);
        $.makeTable($dict_by_bans, PICK_STR);
        $dict_by_bans = null;
        return;
    });

    /*
    ** Pick Table - Display By Total Matches
    */
    $("#pick-by-pick").on('click', function(e)
    {
        var $dict_by_picks = {};
        e.preventDefault();
        $.loadTableDict($pick_table_dict, PICK_STR);
        $dict_by_picks = $.sortByPickRate($pick_table_dict, $curr_role_pick_table);
        $.clearTable(PICK_STR);
        $.makeTable($dict_by_picks, PICK_STR);
        $dict_by_picks = null;
        return;
    });

    /*
    ** Expand Option for Blue Side First Player
    */
    $("#blue-role-add-1").on('click', function(e)
    {
        e.preventDefault();
        $click_count_role_blue[0]++;
        var $side = $.urlSide();
        var $radios = $("#blue-radios-1");
        if ($side == "red"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(1, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_blue[0]);
        if ($click_count_role_blue[0] == 2)
        {
            $click_count_role_blue[0] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Blue Side Second Player
    */
    $("#blue-role-add-4").on('click', function(e)
    {
        e.preventDefault();
        $click_count_role_blue[1]++;

        var $side = $.urlSide();
        var $radios = $("#blue-radios-4");
        if ($side == "red"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(4, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_blue[1]);
        if ($click_count_role_blue[1] == 2)
        {
            $click_count_role_blue[1] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Blue Side Third Player
    */
    $("#blue-role-add-5").on('click', function(e)
    {
        e.preventDefault();
        $click_count_role_blue[2]++;

        var $side = $.urlSide();
        var $radios = $("#blue-radios-5");
        if ($side == "red"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(5, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_blue[2]);
        if ($click_count_role_blue[2] == 2)
        {
            $click_count_role_blue[2] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Blue Side Fourth Player
    */
    $("#blue-role-add-8").click(function(e)
    {
        e.preventDefault();
        $click_count_role_blue[3]++;

        var $side = $.urlSide();
        var $radios = $("#blue-radios-8");
        if ($side == "red"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(8, $pick_dict);
        $.expandRoleOption($radios, $click_count_role_blue[3]);

        if ($click_count_role_blue[3] == 2)
        {
            $click_count_role_blue[3] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Blue Side Fifth Player
    */
    $("#blue-role-add-9").click(function(e)
    {
        e.preventDefault();
        $click_count_role_blue[4]++;

        var $side = $.urlSide();
        var $radios = $("#blue-radios-9");
        if ($side == "red"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(9, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_blue[4]);
        if ($click_count_role_blue[4] == 2)
        {
            $click_count_role_blue[4] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Red Side First Player
    */
    $("#red-role-add-2").click(function(e)
    {
        e.preventDefault();
        $click_count_role_red[0]++;

        var $side = $.urlSide();
        var $radios = $("#red-radios-2");
        if ($side == "blue"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(2, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_red[0]);
        if ($click_count_role_red[0] == 2)
        {
            $click_count_role_red[0] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Red Side Second Player
    */
    $("#red-role-add-3").click(function(e)
    {
        e.preventDefault();
        $click_count_role_red[1]++;

        var $side = $.urlSide();
        var $radios = $("#red-radios-3");
        if ($side == "blue"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(3, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_red[1]);
        if ($click_count_role_red[1] == 2)
        {
            $click_count_role_red[1] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Red Side Third Player
    */
    $("#red-role-add-6").click(function(e)
    {
        e.preventDefault();
        $click_count_role_red[2]++;

        var $side = $.urlSide();
        var $radios = $("#red-radios-6");
        if ($side == "blue"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(6, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_red[2]);
        if ($click_count_role_red[2] == 2)
        {
            $click_count_role_red[2] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Red Side Fourth Player
    */
    $("#red-role-add-7").click(function(e)
    {
        e.preventDefault();
        $click_count_role_red[3]++;

        var $side = $.urlSide();
        var $radios = $("#red-radios-7");
        if ($side == "blue"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(7, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_red[3]);
        if ($click_count_role_red[3] == 2)
        {
            $click_count_role_red[3] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Expand Option for Red Side Five Player
    */
    $("#red-role-add-10").click(function(e)
    {
        e.preventDefault();
        $click_count_role_red[4]++;

        var $side = $.urlSide();
        var $radios = $("#red-radios-10");
        if ($side == "blue"){$(this).attr("src", "/static/img/positions/icon-position-none.png");}
        else{$(this).attr("src", "/static/img/positions/icon-add.png");}

        $.removeRole(10, $pick_dict);

        $.expandRoleOption($radios, $click_count_role_red[4]);
        if ($click_count_role_red[4] == 2)
        {
            $click_count_role_red[4] = 0;
        }
        $radios = null;
        return;
    });

    /*
    ** Select Role - Blue Side
    */
    $("#draft-blue .radios label").click(function(evt)
    {
        evt.preventDefault();
        var $image = $(this).find("img").attr("src");
        var $role = $image.split("-")[2].replace(".png", "");
        var $index = $(this).attr("id").split("-")[4];
        var $div = $("#blue-role-add-" + $index);
        var $radios = $("#blue-radios-" + $index);

        $click_count_role_blue[$blue_pick_array.indexOf(parseInt($index))] = 0;
        $.addRoleToDict($role, $index, "blue", $pick_dict, $blue_pick_array);
        $div.attr("src", $image).css("padding", "4px 4px");
        $.expandRoleOption($radios, 0);

        $image = $role = $index = $div = $radios = null;

        return;
    });

    /*
    ** Select Role - Red Side
    */
    $("#draft-red .radios label").click(function(evt)
    {
        evt.preventDefault();
        var $image = $(this).find("img").attr("src");
        var $role = $image.split("-")[2].replace(".png", "");
        var $index = $(this).attr("id").split("-")[4];
        var $div = $("#red-role-add-" + $index);
        var $radios = $("#red-radios-" + $index);

        $click_count_role_red[$red_pick_array.indexOf(parseInt($index))] = 0;
        $.addRoleToDict($role, $index, "red", $pick_dict, $red_pick_array);
        $div.attr("src", $image).css("padding", "4px 4px");
        $.expandRoleOption($radios, 0);

        $image = $role = $index = $div = $radios = null;

        return;
    });

    /*
    ** Reset Ban Pick - Blue
    */
    $(".holder-blue").click(function(e)
    {
        e.preventDefault();
        if ($(this).css('background-image') != 'none')
        {
            $(this).empty();
            var $champ_img_str = $(this).css('background-image').split("8000")[1].replace("\")", "");
            var $champ = $champ_img_str.split("/")[4].replace(".png", "");
            var $index = $(this).attr("id").split("-")[2];
            var $glow_index = $.getNextKey($ban_dict, 10);
            var $icon_none = $("#draft-table .champ-row .champ-image img[src|='/static/img/positions/icon-position-none-disabled.png");
            delete $ban_dict[$index];
            $ban_table_dict = $.updateTableDictRanks($ban_table_dict, "unban", $champ);

            // reset image
            $(this).css('background-image', '');

            // toggle it in the table
            if ($champ != "icon-position-none-disabled")
            {
                $('.champ-image img[src=\"' + $champ_img_str + '\"').parent().parent().toggle();
            }
            if ($icon_none.parent().parent().is(":hidden")){$icon_none.parent().parent().toggle();}
            // reset glow
            if ($index < $glow_index || $glow_index == null)
            {
                if ($glow_index < 6 && $glow_index > 0)
                {
                    $("#blue-ban-" + $glow_index).empty();
                }
                else if ($glow_index >= 6)
                {
                    $("#red-ban-" + ($glow_index - 5)).empty();
                }
                else if ($glow_index == null)
                {
                    $("#intro h2").empty().append("Ban a Champion");
                }
                $(this).append("<div class=\"bar-blue left\"></div>");
                $(this).append("<div class=\"bar-blue top\"></div>");
                $(this).append("<div class=\"bar-blue right\"></div>");
                $(this).append("<div class=\"bar-blue bottom\"></div>");
            }
            $select_call_count = 0;

            // reset champ select
            $.resetChampGlow(0);
            $.resetChampImage(1, $pick_dict);
            $.resetRoleSelections(1);

            $champ_img_str = $champ = $index = $glow_index = $icon_none = null;
        }
        $.resetTable($ban_table_dict, BAN_STR);
        $.clearDictionary(0, $pick_table_dict);
        $.clearTable(PICK_STR);
        $curr_role_ban_table = "";
        return;
    });

    /*
    ** Reset Ban Pick - Red
    */
    $(".holder-red").click(function(e)
    {
        e.preventDefault();

        if ($(this).css('background-image') != 'none')
        {
            $(this).empty();
            var $champ_img_str = $(this).css('background-image').split("8000")[1].replace("\")", "");
            var $champ = $champ_img_str.split("/")[4].replace(".png", "");
            var $index = (parseInt($(this).attr("id").split("-")[2]) + 5);
            var $glow_index = $.getNextKey($ban_dict, 10);
            var $icon_none = $("#draft-table .champ-row .champ-image img[src|='/static/img/positions/icon-position-none-disabled.png");
            delete $ban_dict[$index];
            $ban_table_dict = $.updateTableDictRanks($ban_table_dict, "unban", $champ);

            // reset image
            $(this).css('background-image', '');

            // toggle it in the table
            if ($champ != "icon-position-none-disabled")
            {
                $('.champ-image img[src=\"' + $champ_img_str + '\"').parent().parent().toggle();
            }
            if ($icon_none.parent().parent().is(":hidden")){$icon_none.parent().parent().toggle();}
            // reset glow
            if ($index < $glow_index || $glow_index == null)
            {
                if ($glow_index < 6 && $glow_index > 0)
                {
                    $("#blue-ban-" + $glow_index).empty();
                }
                else if ($glow_index >= 6)
                {
                    $("#red-ban-" + ($glow_index - 5)).empty();
                }
                else if ($glow_index == null)
                {
                    $("#intro h2").empty().append("Ban a Champion");
                }
                $(this).append("<div class=\"bar-red left\"></div>");
                $(this).append("<div class=\"bar-red top\"></div>");
                $(this).append("<div class=\"bar-red right\"></div>");
                $(this).append("<div class=\"bar-red bottom\"></div>");
            }
            $select_call_count = 0;

            // reset champ select
            $.resetChampGlow(0);
            $.resetChampImage(1, $pick_dict);
            $.resetRoleSelections(1);

            $champ_img_str = $champ = $index = $glow_index = $icon_none = null;
        }
        $.resetTable($ban_table_dict, BAN_STR);
        $.clearDictionary(0, $pick_table_dict);
        $.clearTable(PICK_STR);
        $curr_role_ban_table = "";
        return;
    });

    /*
    ** Reset Champ Select - Blue Side
    */
    $(".btn-blue-side").click(function(e)
    {
        e.preventDefault();
        if ($(this).attr("src").indexOf("icon-position-autofill-protection") == -1)
        {
            var $index = parseInt($(this).attr("id").split("-")[2]);
            var $current_glow = $.getNextKey($pick_dict, 10);

            $.resetChampGlow($index, $current_glow);
            $.resetChampImage($index, $pick_dict);
            $.resetRoleSelections($index);

            $index = $current_glow = null;
        }
        $.clearTable(PICK_STR);
        return;
    });

    /*
    ** Reset Champ Select - Red Side
    */
    $(".btn-red-side").click(function(e)
    {
        e.preventDefault();
        if ($(this).attr("src").indexOf("icon-position-autofill-protection") == -1)
        {
            var $index = parseInt($(this).attr("id").split("-")[2]);
            var $current_glow = $.getNextKey($pick_dict, 10);

            $.resetChampGlow($index, $current_glow);
            $.resetChampImage($index, $pick_dict);
            $.resetRoleSelections($index);

            $index = $current_glow = null;
        }
        $.clearTable(PICK_STR);
        return;
    });

    /*
    ** Select Champion Main
    */
    $(".champ-image").click(function(e)
    {
        e.preventDefault();
        var $image = $(this).find("img").attr("src");
        var $champ = $image.split("/")[4].replace(".png", "");
        var $side = $.urlSide();

        $.resetDraftTable();
        $.loadTableDict($ban_table_dict, BAN_STR);
        $curr_role_ban_table = "";
        $.resetFilterClickCount($click_count_array);

        if ($.isPickDictFull()){ return; }
        if ($champ != "icon-position-none-disabled"){$(this).parent().toggle();}
        if (Object.keys($ban_dict).length <= 9 || jQuery.isEmptyObject($ban_dict))
        {
            $.mainban($champ, $image);
            $ban_table_dict = $.updateTableDictRanks($ban_table_dict, BAN_STR, $champ);
            $.resetTable($ban_table_dict, BAN_STR);
        }
        if (Object.keys($ban_dict).length == 10)
        {
            $.mainSelect($champ, $image);
        }
        $image = $champ = $side = null;

        return;
    });

});

/*
** Add Glow Effect to Object
*/
$.addGlow = function(object, side)
{
    if (side == "blue")
    {
        object.css("-webkit-animation-name", "bluePulse");
        object.css("-webkit-animation-duration", "2s");
        object.css("-webkit-animation-iteration-count", "infinite");
    }
    else if (side == "red")
    {
        object.css("-webkit-animation-name", "redPulse");
        object.css("-webkit-animation-duration", "2s");
        object.css("-webkit-animation-iteration-count", "infinite");
    }
    return;
};

/*
** Add Selected Champion Role to Dictionary
*/
$.addRoleToDict = function(role, index, side, object, array)
{
    var $url_side = $.urlSide();

    // Check if role already taken by another selection - dependent on side
    for (var side_index in array)
    {
        if (object.hasOwnProperty(array[side_index]) && object[array[side_index]][1] === role && array[side_index] != index)
        {
            // Reset in Pick Dict
            object[array[side_index]][1] = "";

            // Reset Role Selection Image
            if ($url_side == side)
            {
                $("#" + side + "-role-add-" + array[side_index]).attr("src", "/static/img/positions/icon-add.png");
            }
            else
            {
                $("#" + side + "-role-add-" + array[side_index]).attr("src", "/static/img/positions/icon-position-none.png");
            }
        }
    }
    if (object.hasOwnProperty(index))
    {
        object[index][1] = role;
        return;
    }
    else
    {
        object[index] = ["", role];
        return;
    }
};

/*
** Wrapper Function around Ajax Call
*/
$.ajaxWrapper = function(method, table_type)
{
    var $side =$.urlSide();
    if (table_type === BAN_STR)
    {
        var $rank = $("#ban-dropdown-rank-meta").children("span").text();
        var $patch = $("#ban-dropdown-patch-meta").children("span").text();
        var $table = $.getBanTableElement();

        $.ajax({
            type: method,
            // Disallow Ajax Global Event Handlers to disable loading animation
            global: false,
            data:
            {
                rank: $rank,
                patch: $patch,
                table: table_type
            },
            // 1 Second Rate Limit on Ajax Requests
            beforeSend: function()
            {
                var can_send = NUMBER_OF_REQUESTS < NUMBER_OF_REQUESTS_ALLOWED;
                NUMBER_OF_REQUESTS++;
                return can_send;
            },
            success: function(result)
            {
                $table.html(result);
                $ban_table_dict = $.clearDictionary(0, $ban_table_dict)
                $.loadTableDict($ban_table_dict, table_type);
                $rank = $patch = $table = null;
                return;
            },
            failure: function()
            {
                console.log("Error.");
                $rank = $patch = $table = null;
                return;
            }
        });
    }
    else if (table_type === PICK_STR)
    {
        var $rank = $("#pick-dropdown-rank-meta").children("span").text();
        var $patch = $("#pick-dropdown-patch-meta").children("span").text();
        var $table = $.getPickTableElement();

        // Check if Pick Dict is empty, if so - update table and return
        if ($.isPickDictEmpty())
        {
            $table.empty();
            $table.append($('<div/>').addClass("nodata").text("A Champion hasn't been selected yet!"));
            return;
        }

        $.ajax({
            type: method,
            // Allow Ajax Global Event Handlers for Loading Animation
            global: true,
            data:
            {
                rank: $rank,
                patch: $patch,
                table: table_type,
                pick_dict: JSON.stringify($pick_dict)
            },
            // 1 Second Rate Limit on Ajax Requests
            beforeSend: function()
            {
                // Check Rate Limit
                var can_send = NUMBER_OF_REQUESTS < NUMBER_OF_REQUESTS_ALLOWED;
                NUMBER_OF_REQUESTS++;
                return can_send;
            },
            success: function(result)
            {
                $table.html(result);
                $.loadTableDict($pick_table_dict, PICK_STR);
                console.log($pick_table_dict);
                $.clearTable(PICK_STR);
                $.makeTable($pick_table_dict, PICK_STR);
                $rank = $patch = $table = null;
                return;
            }
        });
    }
    return;
};

/*
** Clear a Dictionary
*/
$.clearDictionary = function(start_index, object)
{
    for (var key in object)
    {
        if (key >= start_index)
        {
            delete object[key];
        }
    }
    return object;
};

/*
** Clear the Table
*/
$.clearTable = function(table)
{
    var $table = $("." + table + "-table");
    $table.children(".champ-row").each(function()
    {
        $(this).remove();
    });
    $table = null;
    return;
};

/*
** Delete from object at index
*/
$.deleteDicIndex = function(object, index)
{
    if (index in object)
    {
        delete object[index];
    }
    return object;
};

/*
** Show Role Options for Champion Select Event Loop
*/
$.expandRoleOption = function(object, click_count)
{
    if ((click_count % 2) == 1)
    {
        for (var i=1; i<=5; i++)
        {
            object.children(':nth-child(' + i + ')').css("visibility", "visible");
        }
    }
    else
    {
        for (var i=1; i<=5; i++)
        {
            object.children(':nth-child(' + i + ')').css("visibility", "hidden");
        }
    }
    return;
};

/*
** Filter table with Role Filter filter
*/
$.filterRole = function(table, filter)
{
    var $row_elem = $("." + table + "-table .champ-row .role");
    $row_elem.each(function()
    {
        var $role = $(this).find("img").attr("src").split("/")[4].replace("icon-position-", "").replace(".png", "");
        if ($role != filter)
        {
            $(this).parent().toggle();
        }
        $role = null;
    });
    $row_elem = null;
    return;
};

/*
** Fix Champion Strings
*/
$.fixChampString = function(champ_str)
{
    var $champ = champ_str.replace(" ", "");
    $champ = $champ.replace(".", "");
    if ($champ.indexOf("\'") >= 0)
    {
        $champ = $champ.replace("'", "");
        if (jQuery.inArray($champ, ["KogMaw", "RekSai"]) > -1)
        {
            return $champ;
        }
        else
        {
            $champ = $champ.toLowerCase().capitalize();
            return $champ;
        }
    }
    else if (jQuery.inArray($champ, ["Wukong"]) > -1)
    {
        $champ = "MonkeyKing";
        return $champ;
    }
    else if (jQuery.inArray($champ, ["LeBlanc"]) > -1)
    {
        $champ = $champ.toLowerCase().capitalize();
        return $champ;
    }
    return $champ
};

/*
** Retrieve Ban Table Element
*/
$.getBanTableElement = function()
{
    var side = $.urlSide();
    return $("#" + side + "-ban-table");
};

/*
** Get Key of Dictionary by Value
*/
$.getKeyByValue = function(object, value)
{

    return Object.keys(object).find(key => object[key] === value);
};

/*
** Get the next key of dictionary from index
*/
$.getNextKey = function(object, length, exclude)
{
    for (var i=1; i<=length; i++)
    {
        // First index not in object
        if(!(i in object))
        {
          if (exclude == null){return i;}
          else if (i == exclude){continue;}
          else{return i;}
        }
        // If Pick Dict was already initialized at index
        else if (object[i][0] === "")
        {
            return i;
        }
    }
    return;
};

/*
** Retrieve Pick Table Element
*/
$.getPickTableElement = function()
{
    var side = $.urlSide();
    return $("#" + side + "-pick-table");
};

/*
** Transform Image String to Role String
*/
$.imageToRole = function(object)
{
    var image = object.children().attr("src");
    var role = image.split("/")[4].replace("icon-position-", "").replace(".png", "");
    image = null;
    return role;
};

/*
** Initializes the Pick Dictionary
*/
$.initPickDict = function()
{
    if (Object.keys($pick_dict).length === 0)
    {
        $pick_dict["1"] = ["", ""];
    }
    return;
};

/*
** Check if Index in Array
*/
$.isIndexInArray = function(index, array)
{
    if (jQuery.inArray(index, array) > -1)
    {
        return true;
    }
    else
    {
        return false;
    }
};

/*
** Check if Value in Dictionary
*/
$.isInDictionary = function(value, object)
{
    for (var key in object)
    {
        if (object[key] == value)
        {
            return true;
        }
        else if (Array.isArray(object[key]))
        {
            if (object[key].includes(value))
            {
                return true;
            }
        }
    }
    return false;
};

/*
** Check if Pick Dict is Empty
*/
$.isPickDictEmpty = function()
{
    // If No Entries - return True
    if (Object.keys($pick_dict).length == 0)
    {
        return true;
    }

    // If a Champion has been Selected - return false
    for (var index in $pick_dict)
    {
        if ($pick_dict[index][0] != "")
        {
            return false;
        }
    }
    // No Champion Selected - return True
    return true;
};

/*
** Checks if Pick Dict is full
*/
$.isPickDictFull = function()
{
    // check if length less than 10
    if (Object.keys($pick_dict).length < 10)
    {
        return false;
    }

    // Check if each champion string is set
    for (var key in $pick_dict)
    {
        if ($pick_dict[key][0] === "")
        {
            return false;
        }
    }
    return true;
};

/*
** Load Table Dictionary
*/
$.loadTableDict = function(object, table)
{
    if (Object.keys(object).length == 0)
    {
        var index = 0;
        var $table = $("." + table + "-table");
        $table.children(".champ-row").each(function()
        {
            index += 1;
            var $role_object = $(".role", this);
            var rank = $(this).find(".rank span").text(),
                role = $.imageToRole($role_object),
                champ = $(this).find(".champion span").text(),
                winrate = $(this).find(".winrate").text(),
                banrate = $(this).find(".banrate").text(),
                pickrate = $(this).find(".pickrate").text(),
                visibility = $(this).css("display");
            if (!($.isInDictionary(champ, $ban_dict)))
            {
                object[rank] = [role, champ, winrate, banrate, pickrate, visibility, index];
            }
            else
            {
                object[rank] = [role, champ, winrate, banrate, pickrate, visibility, table];
                index -= 1;
            }
            $role_object = rank = role = champ = winrate = banrate = pickrate = visibility = null;
        });
    }
    // TODO - this should return object
    return;
};

/*
** Ban Champion Event Loop
*/
$.mainban = function(champ, champ_img)
{
    var $ban_index = null;
    var $next_ban_index = null;

    if($ban_index == null){$ban_index = $.getNextKey($ban_dict, 10);}
    if ($next_ban_index == null){$next_ban_index = $.getNextKey($ban_dict, 10, $ban_index);}
    if($ban_index != null){$ban_dict[$ban_index] = champ;}

    // Current
    if ($ban_index < 6)
    {
        $("#blue-ban-" + $ban_index).css("background-image", "url(" + champ_img +")");
        $("#blue-ban-" + $ban_index).css("background-size", "cover");
        $("#blue-ban-" + $ban_index).empty();
        $("#blue-ban-" + $ban_index).append("<div class=\"bar-blue left-full\"></div>");
        $("#blue-ban-" + $ban_index).append("<div class=\"bar-blue right-full\"></div>");
        $("#blue-ban-" + $ban_index).append("<div class=\"bar-blue top-full\"></div>");
        $("#blue-ban-" + $ban_index).append("<div class=\"bar-blue bottom-full\"></div>");
    }
    else
    {
        $("#red-ban-" + ($ban_index - 5)).css("background-image", "url(" + champ_img +")");
        $("#red-ban-" + ($ban_index - 5)).css("background-size", "cover");
        $("#red-ban-" + ($ban_index - 5)).empty();
        $("#red-ban-" + ($ban_index - 5)).append("<div class=\"bar-red left-full\"></div>");
        $("#red-ban-" + ($ban_index - 5)).append("<div class=\"bar-red right-full\"></div>");
        $("#red-ban-" + ($ban_index - 5)).append("<div class=\"bar-red top-full\"></div>");
        $("#red-ban-" + ($ban_index - 5)).append("<div class=\"bar-red bottom-full\"></div>");
    }
    // Next
    if ($next_ban_index < 6 && $next_ban_index > 0)
    {
        $("#blue-ban-" + $next_ban_index).append("<div class=\"bar-blue left\"></div>");
        $("#blue-ban-" + $next_ban_index).append("<div class=\"bar-blue right\"></div>");
        $("#blue-ban-" + $next_ban_index).append("<div class=\"bar-blue top\"></div>");
        $("#blue-ban-" + $next_ban_index).append("<div class=\"bar-blue bottom\"></div>");
        return true;
    }
    else if ($next_ban_index >= 6 && $next_ban_index < 11)
    {
        $("#red-ban-" + ($next_ban_index - 5)).append("<div class=\"bar-red left\"></div>");
        $("#red-ban-" + ($next_ban_index - 5)).append("<div class=\"bar-red top\"></div>");
        $("#red-ban-" + ($next_ban_index - 5)).append("<div class=\"bar-red right\"></div>");
        $("#red-ban-" + ($next_ban_index - 5)).append("<div class=\"bar-red bottom\"></div>");
        return true;
    }
    else if ($next_ban_index == false){return false;}

};

/*
** Select Champion Event Loop
*/
$.mainSelect = function(champ, champ_img)
{
    if ($("#intro h2") != "Select a Champion"){$("#intro h2").empty().append("Select a Champion");}
    $select_call_count++;
    if ($select_call_count == 1)
    {
        $.addGlow($("#blue-side-1"), "blue");
        $.initPickDict();
        // hide X icon for champ select phase
        var $icon_none = $("#draft-table .champ-row .champ-image img[src|='/static/img/positions/icon-position-none-disabled.png");
        if ($icon_none.is(":visible"))
        {
            $icon_none.parent().parent().toggle();
        }
        return;
    }

    var $select_index = $.getNextKey($pick_dict, 10);
    // Pick Dict already initialized at index from role selection
    if (Array.isArray($pick_dict[$select_index])){$pick_dict[$select_index][0] = champ;}
    // Create New Entry to Pick Dict
    else{$pick_dict[$select_index] = [champ, ""];}
    var $next_select_index = $.getNextKey($pick_dict, 10, $select_index);

    // Current
    if ($.isIndexInArray(parseInt($select_index), $blue_pick_array))
    {
        var $object = $("#blue-side-" + $select_index.toString());
        $object.attr("src", "");
        $object.css("background-image", "url(" + champ_img +")");
        $object.css("background-size", "cover");
        $.removeGlow($object);
    }
    else if ($.isIndexInArray(parseInt($select_index), $red_pick_array))
    {
        var $object = $("#red-side-" + $select_index.toString());
        $object.attr("src", "");
        $object.css("background-image", "url(" + champ_img +")");
        $object.css("background-size", "cover");
        $.removeGlow($object);
    }
    // Next
    if ($.isIndexInArray(parseInt($next_select_index), $blue_pick_array))
    {
        var $object = $("#blue-side-" + $next_select_index.toString());
        $.addGlow($object, "blue");
        $object = null;
        return;
    }
    else if ($.isIndexInArray(parseInt($next_select_index), $red_pick_array))
    {
        var $object = $("#red-side-" + $next_select_index.toString());
        $.addGlow($object, "red");
        $object = null;
        return;
    }
    return;
};

/*
** Make table based on data in object
*/
$.makeTable = function(object, table)
{
    for (var key in object)
    {
        var champ = $.fixChampString(object[key][1]);
        var rank = (object[key][6]).toString();
        if (rank === table)
        {
            continue;
        }
        else
        {
            var $table = $("." + table + "-table"),
                $row = $('<div/>').addClass("champ-row").css("display", object[key][5]),
                $rank = $('<div/>').addClass("champ-row rank"),
                $role = $('<div/>').addClass("champ-row role"),
                $champ = $('<div/>').addClass("champ-row champion"),
                $winrate = $('<div/>').addClass("champ-row winrate"),
                $banrate = $('<div/>').addClass("champ-row banrate"),
                $pickrate = $('<div/>').addClass("champ-row pickrate"),
                $role_img = $("<img/>").attr("src", "/static/img/positions/icon-position-" + object[key][0] + ".png")
                                       .attr("width", "20")
                                       .attr("height", "20"),
                $champ_img = $("<img/>").attr("src", "/static/img/champion/" + champ + ".png")
                                        .attr("width", "20")
                                        .attr("height", "20");

            $rank.append("<span>" + rank + "</span>");
            $role.append($role_img);
            $champ.append($champ_img).append($("<span/>").text(object[key][1]));
            $winrate.append(object[key][2]);
            $banrate.append(object[key][3]);
            $pickrate.append(object[key][4]);
            $row.append($rank).append($role).append($champ).append($winrate).append($banrate).append($pickrate);
            $table.append($row);

            $table = $row = $rank = $role = $champ = $winrate = $banrate = $pickrate = $role_img = $champ_img = null;
        }
    }
    return;
};

/*
** Remove Glow Effect from Object
*/
$.removeGlow = function(object)
{
    object.css("-webkit-animation-name", "");
    object.css("-webkit-animation-duration", "");
    object.css("-webkit-animation-iteration-count", "");
    return;
};

/*
** Remove Role from Dictionary
*/
$.removeRole = function(index, object)
{
    if(!(object.hasOwnProperty(index)))
    {
        return;
    }
    object[index][1] = "";
    return;
};

/*
** Reset the Champion Glow Effect
*/
$.resetChampGlow = function(index)
{
    var $current_glow = $.getNextKey($pick_dict, 10);
    if (parseInt(index) > 0 && $current_glow == null)
    {
        // New Glow
        if ($.isIndexInArray(parseInt(index), $red_pick_array))
        {
            var $object = $("#red-side-" + index.toString())
            $.addGlow($object, "red");
            $object = null;
            return;
        }
        else if ($.isIndexInArray(parseInt(index), $blue_pick_array))
        {
            var $object = $("#blue-side-" + index.toString())
            $.addGlow($object, "blue");
            $object = null;
            return;
        }
    }
    else if (parseInt(index) == 0 && $current_glow == null)
    {
        return;
    }
    else if (parseInt(index) == 0 && $current_glow != null)
    {
        // Current Glow
        if ($.isIndexInArray(parseInt($current_glow), $red_pick_array))
        {
            var $object = $("#red-side-" + $current_glow.toString())
            $.removeGlow($object);
            $object = null;
            return;
        }
        else if ($.isIndexInArray(parseInt($current_glow), $blue_pick_array))
        {
            var $object = $("#blue-side-" + $current_glow.toString())
            $.removeGlow($object);
            $object = null;
            return;
        }
    }
    else if( parseInt(index) < parseInt($current_glow))
    {
        // Current Glow
        if ($.isIndexInArray(parseInt($current_glow), $red_pick_array))
        {
            var $object = $("#red-side-" + $current_glow.toString())
            $.removeGlow($object);
        }
        else if ($.isIndexInArray(parseInt($current_glow), $blue_pick_array))
        {
            var $object = $("#blue-side-" + $current_glow.toString())
            $.removeGlow($object);
        }
        // New Glow
        if ($.isIndexInArray(parseInt(index), $red_pick_array))
        {
            var $object = $("#red-side-" + index.toString())
            $.addGlow($object, "red");
            $object = null;
            return;
        }
        else if ($.isIndexInArray(parseInt(index), $blue_pick_array))
        {
            var $object = $("#blue-side-" + index.toString())
            $.addGlow($object, "blue");
            $object = null;
            return;
        }
    }
    return;
};

/*
** Reset Champion Image in Champion Select
*/
$.resetChampImage = function(index, dictionary)
{
    var $start_index = parseInt(index);

    for (var item in dictionary)
    {
        if ($.isIndexInArray(parseInt(item), $red_pick_array) && parseInt(item) >= $start_index)
        {
            var $object = $("#red-side-" + item.toString());
            if ($object.attr("src") != "/static/img/positions/icon-position-autofill-protection.png" && $object.css("background-image") != "")
            {
                $.resetChampInTable($object);
                $object.css("background-image", "");
                $object.attr("src", "/static/img/positions/icon-position-autofill-protection.png").attr("width", "70").attr("height", "70");
            }
            else{continue;}
        }
        else if ($.isIndexInArray(parseInt(item), $blue_pick_array) && parseInt(item) >= $start_index)
        {
            var $object = $("#blue-side-" + item.toString());
            if ($object.attr("src") != "/static/img/positions/icon-position-autofill-protection.png" && $object.css("background-image") != "")
            {
                $.resetChampInTable($object);
                $object.css("background-image", "");
                $object.attr("src", "/static/img/positions/icon-position-autofill-protection.png").attr("width", "70").attr("height", "70");
            }
            else{continue;}
        }
        else{continue;}
    }
    $pick_dict = $.clearDictionary($start_index, $pick_dict);
    return;
};

/*
** Re-Show Champion in Table
*/
$.resetChampInTable = function(object)
{
    if (object.css("background-image") != "" || object.css("background-image") != null)
    {
        var $champ = object.css("background-image").split("/")[6].replace(".png\")", "");
    }
    else if (object.find("img").attr("src") != "")
    {
        var $champ = object.find("img").attr("src").split("/")[4].replace(".png", "");
    }
    else if (object.attr("src") != "")
    {
        var $champ = object.attr("src").split("/")[4].replace(".png", "");
    }
    var $champ_row_img = $("#draft-table .champ-row .champ-image img[src|='/static/img/champion/" + $champ +".png");
    $champ_row_img.parent().parent().toggle();
    $champ_row_img = null;
    $champ = null;
    return;
};

/*
** Reset the Draft Table
*/
$.resetDraftTable = function()
{
    var $search = $("#filtered-search");
    var $draft_table_hidden = $("#draft-table td:hidden");
    var $draft_table = $("#draft-table td");

    $search.val("");
    $draft_table_hidden.toggle();
    $draft_table.each(function()
    {
        var $champ = $(this).find("img").attr("src").split("/")[4].replace(".png", "");
        if (($.isInDictionary($champ, $ban_dict) || $.isInDictionary($champ, $pick_dict)) && $champ != "icon-position-none-disabled")
        {

            $(this).toggle();
        }
        if ($champ == "icon-position-none-disabled" && Object.keys($ban_dict).length == 10)
        {
            if ($(this).is(":visible"))
            {
                $(this).toggle();
            }
        }
        $champ = null;
    });
    $search = $draft_table_hidden = $draft_table = null;
    return;
};

/*
** Reset Ban Table Filter Click Counts
*/
$.resetFilterClickCount = function(array, exclude)
{
    for (var i=0; i<5; i++)
    {
        if (i == exclude)
        {
            continue;
        }
        else
        {
            array[i] = 0;
        }
    }
    return;
};

/*
** Reset Selected Roles
*/
$.resetRoleSelections = function(start_index)
{
    for (var i=start_index; i<11; i++)
    {
        if ($.isIndexInArray(parseInt(i), $red_pick_array))
        {
            var $role_object = $("#red-role-add-" + i.toString());
            if ($.urlSide() === "red" && $role_object.attr("src") != "/static/img/positions/icon-add.png")
            {
                $role_object.attr("src", "/static/img/positions/icon-add.png");
            }
            else if ($.urlSide() === "blue" && $role_object.attr("src") != "/static/img/positions/icon-position-none.png")
            {
                $role_object.attr("src", "/static/img/positions/icon-position-none.png");
            }
        }
        else if ($.isIndexInArray(parseInt(i), $blue_pick_array))
        {
            var $role_object = $("#blue-role-add-" + i.toString());
            if ($.urlSide() === "red" && $role_object.attr("src") != "/static/img/positions/icon-position-none.png")
            {
                $role_object.attr("src", "/static/img/positions/icon-position-none.png");
            }
            else if ($.urlSide() === "blue" && $role_object.attr("src") != "/static/img/positions/icon-add.png")
            {
                $role_object.attr("src", "/static/img/positions/icon-add.png");
            }
        }
        else{continue;}
    }
    return;
};

/*
** Reset the Table
*/
$.resetTable = function(object, table)
{
    $.loadTableDict(object, table);
    $.clearTable(table);
    $.makeTable(object, table);
    return;
};

/*
** Sort Ban Dictionary by Ban Rate / Pick Dictionary By Wins
*/
$.sortByBanRate = function(object, curr_role)
{
    var $temp_dict = {};

    // load dictionary into array
    var items = Object.keys(object).map(function(key)
    {
        return [key, object[key]];
    });

    // sort items array
    items.sort(function(first, second)
    {
        var f_ban = parseFloat(first[1][3].replace("%", "")),
            s_ban = parseFloat(second[1][3].replace("%", ""));
        if (f_ban < s_ban){return 1;}
        if (f_ban > s_ban){return -1;}
        return 0;
    });

    // load array into dictionary
    if (curr_role != "")
    {
        for (var item of items)
        {
            if (item[1][0] == curr_role)
            {
                $temp_dict["_" + item[0].toString()] = item[1];
            }
        }
    }
    else
    {
        for (var item of items)
        {
            $temp_dict["_" + item[0].toString()] = item[1];
        }
    }
    items = null;
    return $temp_dict;
};

/*
** Sort Dictionary by Champion Name
*/
$.sortByChamp = function(object, curr_role)
{
    var $temp_dict = {};
    // load dictionary into array
    var items = Object.keys(object).map(function(key)
    {
        return [key, object[key]];
    });

    // sort array alphabetically
    items.sort(function(first, second)
    {
        if (first[1][1] < second[1][1]){ return -1;}
        if (first[1][1] > second[1][1]){ return 1;}
        return 0;
    });

    // load array into dictionary
    if (curr_role != "")
    {
        for (var item of items)
        {
            if (item[1][0] == curr_role)
            {
                $temp_dict["_" + item[0].toString()] = item[1];
            }
        }
    }
    else
    {
        for (var item of items)
        {
            $temp_dict["_" + item[0].toString()] = item[1];
        }
    }
    items = null;
    return $temp_dict;
};

/*
** Sort Ban Dictionary by Pick Rate / Pick Dictionary By Total Matches
*/
$.sortByPickRate = function(object, curr_role)
{
    var $temp_dict = {};

    // load dictionary into array
    var items = Object.keys(object).map(function(key)
    {
        return [key, object[key]];
    });

    // sort items array
    items.sort(function(first, second)
    {
        var f_ban = parseFloat(first[1][4].replace("%", "")),
            s_ban = parseFloat(second[1][4].replace("%", ""));
        if (f_ban < s_ban){return 1;}
        if (f_ban > s_ban){return -1;}
        return 0;
    });

    // load array into dictionary
    if (curr_role != "")
    {
        for (var item of items)
        {
            if (item[1][0] == curr_role)
            {
                $temp_dict["_" + item[0].toString()] = item[1];
            }
        }
    }
    else
    {
        for (var item of items)
        {
            $temp_dict["_" + item[0].toString()] = item[1];
        }
    }
    items = null;
    return $temp_dict;
};

/*
** Sort Ban/Pick Dictionary by Champion Rank
*/
$.sortByRank = function(object, curr_role)
{
    var $temp_dict = {},
        keys = Object.keys(object);

    keys.sort();
    var key_length = keys.length
    if (curr_role != "")
    {
        for (var i=0; i<key_length; i++)
        {
            if (object[keys[i]][0] == curr_role)
            {
                $temp_dict[keys[i]] = object[keys[i]];
            }
        }
    }
    else
    {
        for (var i=0; i<key_length; i++)
        {
            $temp_dict[keys[i]] = object[keys[i]];
        }
    }
    items = null;
    return $temp_dict;
};

/*
** Sort Dictionary by Champion Role
*/
$.sortByRole = function(object, curr_role)
{
    var $temp_dict = {},
        keys = Object.keys(object);
    var key_length = keys.length;
    if (curr_role != "")
    {
        for (var i=0; i<key_length; i++)
        {
            var key = keys[i];
            if (object[key][0] == curr_role)
            {
                var temp_array = object[key];
                $temp_dict["_" + key.toString()] = temp_array;
            }
        }
        keys = temp_array = null;
        return $temp_dict;
    }
    else
    {
        // Top
        for (var i=0; i<key_length; i++)
        {
            var key = keys[i];
            if (object[key][0] == "top")
            {
                var temp_array = object[key];
                $temp_dict["_" + key.toString()] = temp_array;
            }
        }
        // Jungle
        for (var i=0; i<key_length; i++)
        {
            var key = keys[i];
            if (object[key][0] == "jungle")
            {
                var temp_array = object[key];
                $temp_dict["_" + key.toString()] = temp_array;
            }
        }
        // Middle
        for (var i=0; i<key_length; i++)
        {
            var key = keys[i];
            if (object[key][0] == "middle")
            {
                var temp_array = object[key];
                $temp_dict["_" + key.toString()] = temp_array;
            }
        }
        // Bottom
        for (var i=0; i<key_length; i++)
        {
            var key = keys[i];
            if (object[key][0] == "bottom")
            {
                var temp_array = object[key];
                $temp_dict["_" + key.toString()] = temp_array;
            }
        }
        // Support
        for (var i=0; i<key_length; i++)
        {
            var key = keys[i];
            if (object[key][0] == "utility")
            {
                var temp_array = object[key];
                $temp_dict["_" + key.toString()] = temp_array;
            }
        }
        temp_array = keys = null;
        return $temp_dict;
    }
};

/*
** Sort Dictionary by Win Rate
*/
$.sortByWinRate = function(object, curr_role)
{
    var $temp_dict = {};

    // load dictionary into array
    var items = Object.keys(object).map(function(key)
    {
        return [key, object[key]];
    });

    // sort items array
    items.sort(function(first, second)
    {
        var f_win = parseFloat(first[1][2].replace("%", "")),
            s_win = parseFloat(second[1][2].replace("%", ""));
        if (f_win < s_win){return 1;}
        if (f_win > s_win){return -1;}
        return 0;
    });

    // load array into dictionary
    if (curr_role != "")
    {
        for (var item of items)
        {
            if (item[1][0] == curr_role)
            {
                $temp_dict["_" + item[0].toString()] = item[1];
            }
        }
    }
    else
    {
        for (var item of items)
        {
            $temp_dict["_" + item[0].toString()] = item[1];
        }
    }
    items = null;
    return $temp_dict;
};

/*
** Capatalize a String
*/
String.prototype.capitalize = function()
{

    return this.charAt(0).toUpperCase() + this.slice(1);
};

/*
** Switch Current Role String
*/
$.switchCurrRole = function(curr_role, role_str)
{
    if (curr_role === role_str){return "";}
    else{return role_str;}
};

/*
** Update Ranks in table dict
*/
$.updateTableDictRanks = function(object, option, champ)
{
    var rank_count = 1;
    for (var key in object)
    {
        if (object[key][1] === champ)
        {
            if (option === "unban")
            {
                object[key][6] = rank_count;
                rank_count++;
            }
            else
            {
                object[key][6] = option;
            }

        }
        else if (object[key][6] === option)
        {
            continue;
        }
        else
        {
            object[key][6] = rank_count;
            rank_count++;
        }
    }
    return object;
};

/*
** Current Side from URL
*/
$.urlSide = function()
{
    var $pathname = window.location.pathname.split('/')[2];
    return ($pathname);
};