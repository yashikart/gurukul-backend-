
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://wcihrkaisrxwxhrlhnax.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndjaWhya2Fpc3J4d3hocmxobmF4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MDQxNzIsImV4cCI6MjA4MjI4MDE3Mn0.xnUnvC-AnpA2j-92IVcd0dYiLxkEzWG171kLygKxHnU'

const supabase = createClient(supabaseUrl, supabaseKey)

async function testConnection() {
    console.log("Testing connection to Supabase...")
    // We try to sign in with a fake user. 
    // If we get "Invalid login credentials", it means we reached the server successfully.
    // If we get "apikey invalid" or network error, then connection is broken.
    const { data, error } = await supabase.auth.signInWithPassword({
        email: 'test_connection_dummy@example.com',
        password: 'wrong_password_123'
    })

    if (error) {
        console.log(`Connection Result: ${error.message}`)
        if (error.message === 'Invalid login credentials') {
            console.log("SUCCESS: Connected to Supabase Auth service (Server rejected fake credentials as expected).")
        } else {
            console.log("WARNING: Unexpected error message. Please check config.")
        }
    } else {
        console.log("Unexpected success with fake credentials?")
    }
}

testConnection()
