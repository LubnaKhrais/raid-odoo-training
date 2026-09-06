# Bike Management

## Project Overview

Bike Management is a custom Odoo 19 Community Edition module developed for Rami's Bike Workshop.

The module provides a simple system for managing the workshop's bike fleet and storing the information required for daily rental operations.

## Requirements

The module manages the following bike information:

- Bike Name / Code
- Brand
- Bike Type
- Purchase Date
- Last Maintenance Date
- Daily Rental Price
- Wheel Size (inches)

### Bike Types

The Bike Type field provides the following options:

- Road
- Mountain
- City
- Electric

## Features

### Bike Management

Users can create, view, edit, and delete bike records according to their access permissions.

### List View

The Bike List View displays:

- Bike Name / Code
- Brand
- Bike Type
- Purchase Date
- Last Maintenance Date
- Daily Rental Price
- Wheel Size

### Form View

The Bike Form View provides all required fields for creating and managing individual bike records.

### Access Control

Bike management is restricted to users belonging to the Bike Workshop Staff security group.

The Administrator is configured with Workshop Staff permissions by default.

## Technical Details

- Odoo Version: 19 Community Edition
- Module Name: `bike_management`
- Model: `bike.management.bike`
- License: LGPL-3

## Module Structure

```text
bike_management/
├── __init__.py
├── __manifest__.py
├── hooks.py
├── models/
│   ├── __init__.py
│   └── bike.py
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
└── views/
    └── bike_views.xml
