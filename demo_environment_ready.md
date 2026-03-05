# Demo Environment Ready

## Architecture Setup Complete
The dedicated Demo Architecture for Gurukul has been successfully provisioned. 
This environment is isolated to ensure safe and controlled demonstration flows.

**Tenant URL:**
`demo.gurukul.blackholeinfiverse.com`

**Tenant ID:**
Created in the central database as an `INSTITUTION` type.

## Demo Accounts (Credentials)

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@demo.com` | `demo123` |
| **Teacher** | `teacher@demo.com` | `demo123` |
| **Parent** | `parent@demo.com` | `demo123` |
| **Student** | `student@demo.com` | `demo123` |

## Data Population
* `Demo Class 10-A` cohort has been created.
* The Student is assigned to the Cohort and linked to the Parent account.
* The Teacher is assigned to the Student for the subject "Science".
* Dummy `SubjectData` (Science/Photosynthesis) has been populated for the Student.

## Data Isolation & Telemetry
The demo dataset is contained strictly within the `demo.gurukul.blackholeinfiverse.com` tenant. Telemetry and Analytics exports are filtered by `tenant_id` to ensure production data is not affected by demo interactions. 
This dataset is now **Frozen** for presentations.
