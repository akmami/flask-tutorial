db.createUser(
    {
        user: "admin",
        pwd: "passw1234",
        roles: [
            {
                role: "readWrite",
                db: "flaskdb"
            }
        ]
    }
)