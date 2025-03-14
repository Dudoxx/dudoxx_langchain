"""
Command-Line Interface for Automated Large-Text Field Extraction Solution

This module provides a command-line interface for the extraction pipeline.
"""

import os
import sys
import json
import argparse
import asyncio
from typing import List, Dict, Any, Optional

# Import client library
try:
    from client import ExtractionClientSync
except ImportError:
    # When installed as a package
    from dudoxx_extraction.client import ExtractionClientSync


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Automated Large-Text Field Extraction Solution",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract information from a file")
    extract_parser.add_argument("file", help="Path to the file to extract from")
    extract_parser.add_argument("--domain", "-d", required=True, help="Domain context")
    extract_parser.add_argument("--fields", "-f", required=True, nargs="+", help="Fields to extract")
    extract_parser.add_argument("--output", "-o", default="output.json", help="Output file path")
    extract_parser.add_argument("--format", choices=["json", "text", "xml"], default="json", help="Output format")
    extract_parser.add_argument("--config-dir", default="./config", help="Configuration directory")
    
    # Extract text command
    extract_text_parser = subparsers.add_parser("extract-text", help="Extract information from text")
    extract_text_parser.add_argument("--text", "-t", required=True, help="Text to extract from")
    extract_text_parser.add_argument("--domain", "-d", required=True, help="Domain context")
    extract_text_parser.add_argument("--fields", "-f", required=True, nargs="+", help="Fields to extract")
    extract_text_parser.add_argument("--output", "-o", default="output.json", help="Output file path")
    extract_text_parser.add_argument("--format", choices=["json", "text", "xml"], default="json", help="Output format")
    extract_text_parser.add_argument("--config-dir", default="./config", help="Configuration directory")
    
    # List domains command
    domains_parser = subparsers.add_parser("list-domains", help="List available domains")
    domains_parser.add_argument("--config-dir", default="./config", help="Configuration directory")
    
    # List fields command
    fields_parser = subparsers.add_parser("list-fields", help="List fields for a domain")
    fields_parser.add_argument("--domain", "-d", required=True, help="Domain name")
    fields_parser.add_argument("--config-dir", default="./config", help="Configuration directory")
    
    # Init config command
    init_config_parser = subparsers.add_parser("init-config", help="Initialize configuration")
    init_config_parser.add_argument("--output-dir", default="./config", help="Output directory")
    
    # API server command
    api_parser = subparsers.add_parser("api", help="Start API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    api_parser.add_argument("--workers", type=int, default=4, help="Number of worker processes")
    api_parser.add_argument("--config-dir", default="./config", help="Configuration directory")
    
    return parser


def extract_command(args: argparse.Namespace) -> None:
    """
    Extract information from a file.
    
    Args:
        args: Command-line arguments
    """
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    # Initialize client
    client = ExtractionClientSync(config_dir=args.config_dir)
    
    try:
        # Extract information
        result = client.extract_file(
            file_path=args.file,
            fields=args.fields,
            domain=args.domain,
            output_formats=[args.format]
        )
        
        # Get output
        if args.format == "json":
            output = result.get("json_output", {})
            output_str = json.dumps(output, indent=2)
        elif args.format == "text":
            output_str = result.get("text_output", "")
        elif args.format == "xml":
            output_str = result.get("xml_output", "")
        else:
            print(f"Error: Unsupported format: {args.format}")
            sys.exit(1)
        
        # Write output to file
        with open(args.output, "w") as f:
            f.write(output_str)
        
        # Print metadata
        print(f"Extraction completed successfully.")
        print(f"Output written to: {args.output}")
        print(f"Processing time: {result.get('metadata', {}).get('processing_time', 0):.2f} seconds")
        print(f"Chunk count: {result.get('metadata', {}).get('chunk_count', 0)}")
        print(f"Token count: {result.get('metadata', {}).get('token_count', 0)}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def extract_text_command(args: argparse.Namespace) -> None:
    """
    Extract information from text.
    
    Args:
        args: Command-line arguments
    """
    # Initialize client
    client = ExtractionClientSync(config_dir=args.config_dir)
    
    try:
        # Extract information
        result = client.extract_text(
            text=args.text,
            fields=args.fields,
            domain=args.domain,
            output_formats=[args.format]
        )
        
        # Get output
        if args.format == "json":
            output = result.get("json_output", {})
            output_str = json.dumps(output, indent=2)
        elif args.format == "text":
            output_str = result.get("text_output", "")
        elif args.format == "xml":
            output_str = result.get("xml_output", "")
        else:
            print(f"Error: Unsupported format: {args.format}")
            sys.exit(1)
        
        # Write output to file
        with open(args.output, "w") as f:
            f.write(output_str)
        
        # Print metadata
        print(f"Extraction completed successfully.")
        print(f"Output written to: {args.output}")
        print(f"Processing time: {result.get('metadata', {}).get('processing_time', 0):.2f} seconds")
        print(f"Chunk count: {result.get('metadata', {}).get('chunk_count', 0)}")
        print(f"Token count: {result.get('metadata', {}).get('token_count', 0)}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def list_domains_command(args: argparse.Namespace) -> None:
    """
    List available domains.
    
    Args:
        args: Command-line arguments
    """
    # Initialize client
    client = ExtractionClientSync(config_dir=args.config_dir)
    
    try:
        # Get domains
        domains = client.get_domains()
        
        # Print domains
        print("Available domains:")
        for domain in domains:
            print(f"- {domain['name']}: {domain['description']}")
            print(f"  Fields: {', '.join(domain['fields'])}")
            print()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def list_fields_command(args: argparse.Namespace) -> None:
    """
    List fields for a domain.
    
    Args:
        args: Command-line arguments
    """
    # Initialize client
    client = ExtractionClientSync(config_dir=args.config_dir)
    
    try:
        # Get fields
        fields = client.get_domain_fields(args.domain)
        
        # Print fields
        print(f"Fields for domain '{args.domain}':")
        for field in fields:
            print(f"- {field['name']}: {field['description']}")
            print(f"  Type: {field['type']}")
            print(f"  Unique: {field['is_unique']}")
            print()
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def init_config_command(args: argparse.Namespace) -> None:
    """
    Initialize configuration.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Import configuration service
        try:
            from configuration_service import create_default_config
        except ImportError:
            # When installed as a package
            from dudoxx_extraction.configuration_service import create_default_config
        
        # Create default configuration
        create_default_config(args.output_dir)
        
        print(f"Configuration initialized successfully in: {args.output_dir}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def api_command(args: argparse.Namespace) -> None:
    """
    Start API server.
    
    Args:
        args: Command-line arguments
    """
    try:
        # Import API service
        try:
            from api_service import app
        except ImportError:
            # When installed as a package
            from dudoxx_extraction.api_service import app
        
        # Import uvicorn
        import uvicorn
        
        # Start API server
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            workers=args.workers
        )
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def main() -> None:
    """Main function."""
    # Create parser
    parser = create_parser()
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "extract":
        extract_command(args)
    elif args.command == "extract-text":
        extract_text_command(args)
    elif args.command == "list-domains":
        list_domains_command(args)
    elif args.command == "list-fields":
        list_fields_command(args)
    elif args.command == "init-config":
        init_config_command(args)
    elif args.command == "api":
        api_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
