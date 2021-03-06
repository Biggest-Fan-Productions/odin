/**
    Copyright 2016-2019 Red Anchor Trading Co. Ltd.

    Distributed under the Boost Software License, Version 1.0.
    See <http://www.boost.org/LICENSE_1_0.txt>
 */

#include <fostgres/sql.hpp>

#include <odin/app.hpp>
#include <odin/odin.hpp>

#include <fost/insert>
#include <fost/log>
#include <fostgres/sql.hpp>


fostlib::json odin::app::get_detail(
        fostlib::pg::connection &cnx, const f5::u8view app_id) {
    static const f5::u8view sql(
            "SELECT "
            "odin.app.tableoid AS app__tableoid, odin.app.* "
            "FROM odin.app "
            "WHERE odin.app.app_id = $1");

    auto data = fostgres::sql(cnx, sql, std::vector<fostlib::string>{app_id});
    auto &rs = data.second;
    auto row = rs.begin();
    if (row == rs.end()) {
        fostlib::log::warning(c_odin)("", "App not found")("app_id", app_id);
        return fostlib::json();
    }
    auto record = *row;
    fostlib::json app;
    for (std::size_t index{0}; index < record.size(); ++index) {
        const auto parts = fostlib::split(data.first[index], "__");
        if (parts.size() && parts[parts.size() - 1] == "tableoid") continue;
        fostlib::jcursor pos;
        for (const auto &p : parts) pos /= p;
        fostlib::insert(app, pos, record[index]);
    }
    return app;
}


std::pair<fostlib::utf8_string, fostlib::timestamp> odin::app::mint_user_jwt(
        const f5::u8view identity_id,
        const f5::u8view app_id,
        const fostlib::timediff expires,
        fostlib::json payload) {
    fostlib::jwt::mint jwt{fostlib::jwt::alg::HS256, std::move(payload)};
    jwt.subject(identity_id);
    const fostlib::string jwt_iss = odin::c_app_namespace.value() + app_id;
    jwt.claim("iss", fostlib::json{jwt_iss});
    auto exp = jwt.expires(expires, false);
    auto const jwt_secret = odin::c_jwt_secret.value() + app_id;
    const auto jwt_token = fostlib::utf8_string(jwt.token(jwt_secret.data()));
    return std::make_pair(jwt_token, exp);
}


void odin::app::save_app_user(
        fostlib::pg::connection &cnx,
        f5::u8view reference,
        const f5::u8view app_id,
        const f5::u8view identity_id,
        const f5::u8view app_user_id) {
    fostlib::json app_user_values;
    fostlib::insert(app_user_values, "reference", reference);
    fostlib::insert(app_user_values, "app_id", app_id);
    fostlib::insert(app_user_values, "identity_id", identity_id);
    fostlib::insert(app_user_values, "app_user_id", app_user_id);
    cnx.insert("odin.app_user_ledger", app_user_values);
}


fostlib::json odin::app::get_app_user(
        fostlib::pg::connection &cnx,
        const f5::u8view app_id,
        const f5::u8view identity_id) {
    static const f5::u8view sql(
            "SELECT "
            "odin.app_user.tableoid AS app__tableoid, odin.app_user.* "
            "FROM odin.app_user "
            "WHERE odin.app_user.app_id = $1 "
            "AND odin.app_user.identity_id = $2");

    auto data = fostgres::sql(
            cnx, sql, std::vector<fostlib::string>{app_id, identity_id});
    auto &rs = data.second;
    auto row = rs.begin();
    if (row == rs.end()) {
        fostlib::log::warning(c_odin)("", "User or App not found")(
                "app_id", app_id)("identity_id", identity_id);
        return fostlib::json();
    }
    auto record = *row;
    fostlib::json app_user;
    for (std::size_t index{0}; index < record.size(); ++index) {
        const auto parts = fostlib::split(data.first[index], "__");
        if (parts.size() && parts[parts.size() - 1] == "tableoid") continue;
        fostlib::jcursor pos;
        for (const auto &p : parts) pos /= p;
        fostlib::insert(app_user, pos, record[index]);
    }
    return app_user;
}


fostlib::nullable<fostlib::string> odin::app::get_app_user_identity_id(
        fostlib::pg::connection &cnx,
        f5::u8view const app_id,
        f5::u8view const app_user_id) {
    static fostlib::string const sql(
            "SELECT identity_id "
            "FROM odin.app_user "
            "WHERE odin.app_user.app_id=$1 "
            "AND odin.app_user.app_user_id=$2;");

    auto data = cnx.procedure(sql).exec(
            std::vector<fostlib::string>{app_id, app_user_id});
    auto row = data.begin();
    if (row == data.end()) {
        fostlib::log::warning(c_odin)("", "App user or App not found")(
                "app_id", app_id)("app_user_id", app_user_id);
        return fostlib::null;
    }
    return fostlib::coerce<fostlib::string>((*row)[0]);
}


void odin::app::set_installation_id(
        fostlib::pg::connection &cnx,
        f5::u8view reference,
        f5::u8view app_id,
        f5::u8view identity_id,
        f5::u8view installation_id) {
    fostlib::json user_values;
    fostlib::insert(user_values, "reference", reference);
    fostlib::insert(user_values, "app_id", app_id);
    fostlib::insert(user_values, "identity_id", identity_id);
    fostlib::insert(user_values, "installation_id", installation_id);
    cnx.insert("odin.app_user_installation_id_ledger", user_values);
}
