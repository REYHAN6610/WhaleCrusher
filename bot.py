import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import concurrent.futures
import time
import random
import urllib3
from fake_useragent import UserAgent
import os
import socket
import math
import datetime
from colorama import Fore, Style, init
import re
import sys
import json

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AdvancedWebMiner:
    def __init__(self, max_threads=8, timeout=3, max_depth=1):
        self.max_threads = max_threads
        self.timeout = timeout
        self.max_depth = max_depth
        self.visited_urls = set()
        self.valid_urls = []
        self.other_urls = []
        self.error_urls = []
        self.parameters_found = {}
        self.target_url = ""
        self.start_time = 0
        self.headers = {
            'User-Agent': UserAgent().random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        self.common_php_files = [
            'index.php', 'admin.php', 'login.php', 'config.php', 'user.php',
            'profile.php', 'search.php', 'contact.php', 'about.php', 'product.php',
            'category.php', 'view.php', 'edit.php', 'delete.php', 'add.php',
            'upload.php', 'download.php', 'register.php', 'logout.php', 'cart.php',
            'api.php', 'ajax.php', 'wp-admin.php', 'wp-login.php', 'config.inc.php',
            'setup.php', 'install.php'
        ]
        
        self.common_params = ['id', 'page', 'view', 'category', 'product', 'user', 
                             'search', 'q', 'file', 'action', 'type', 'mode', 'cmd',
                             'command', 'dir', 'path', 'name', 'email', 'password',
                             'username', 'key', 'token', 'session', 'auth', 'admin']
        
        self.fuzzing_items = [
            "index.php", "admin.php", "login.php", "config.php", "config.inc.php",
            "setup.php", "install.php", ".env", "wp-config.php", "wp-login.php",
            "wp-admin/", "xmlrpc.php", "api.php", "api/", "robots.txt", "sitemap.xml",
            ".git/", ".git/config", ".gitignore", ".env.example", "database.sql",
            "backup.sql", "backup/", "uploads/", "upload.php", "files/", "download.php",
            "download/", "download.zip", ".htaccess", ".htpasswd", "manager/", "admin/",
            "admin/login.php", "adminpanel/", "dashboard.php", "user.php", "users.php",
            "register.php", "logout.php", "profile.php", "settings.php", "config.json",
            "config.yml", "composer.json", "package.json", "package-lock.json", "vendor/",
            "node_modules/", ".DS_Store", "favicon.ico", "api/v1/", "api/v2/", "ajax.php",
            "include.php", "includes/", "inc/", "lib/", "class.php", "classes/", "cron.php",
            "cron/", "webhook/", "webhook.php", "payments/", "checkout.php", "cart.php",
            "order.php", "invoice.php", "search.php", "sitemap.php", "contact.php",
            "contact-us.php", "about.php", "terms.php", "privacy.php", ".env.local",
            ".env.production", "secrets.json", "database.yml", "sql/", "dump.sql", "dump/",
            "old/", "backup.tar.gz", "logs/", "error_log", "debug.php", "test.php", "dev/",
            "staging/", "api-docs/", "swagger.json", "swagger.yaml", "oauth/", "token.php",
            "auth.php", "session.php", "session/", ".well-known/security.txt", "adminer.php",
            "phpinfo.php", ".env.back", ".env.old", "config.php.old", "config.bak.php",
            "database_backup.sql", "export.sql", "db.sql", "backup_db.sql", "mysql.sql",
            "sql_dump.sql", "sitemap_index.xml", "sitemap.xml.gz", "robots-backup.txt",
            "license.txt", "README.md", "README.html", "CHANGELOG.md", "LICENSE.txt",
            "install.log", "install.sh", "upgrade.php", "upgrade.sh", "maintenance.php",
            "maintenance.html", "coming_soon.html", "404.php", "403.php", "500.php",
            "phpmyadmin/", "pma/", "phpMyAdmin/", "setup.sql", "sql_backup.tar.gz",
            "db_backup.tar", "credentials.txt", "aws_credentials", ".aws/credentials",
            "id_rsa", "id_rsa.pub", "private.pem", "private.key", "cert.pem", "certificate.crt",
            "ssl/", "ssl_cert/", "kubernetes/", "kubeconfig", "docker-compose.yml", "Dockerfile",
            ".dockerignore", ".gitlab-ci.yml", ".travis.yml", "circleci/config.yml", ".env.example.local",
            ".npmrc", "yarn.lock", "gulpfile.js", "Gruntfile.js", "webpack.config.js", ".htaccess.bak",
            "web.config", "iisconfig.xml", ".bash_history", ".ssh/authorized_keys", ".ssh/id_rsa",
            ".ssh/", ".ftpconfig", "database.yml.bak", "settings.php", "wp-content/", "wp-includes/",
            "wp-config.php.bak", "backup.tar", "backup.zip.enc", "logs/access.log", "logs/error.log",
            "access.log.1", "error.log.1", "debug.log", ".env.secret", "secrets.yml", ".htpasswd.bak",
            "sitemap_old.xml", ".well-known/", ".well-known/acme-challenge/", ".well-known/pki-validation/",
            "api/swagger-ui/", "docs/", "docs/index.html", "api-docs.json", "openapi.yaml", "openapi.json",
            ".env~", "config.php~", "backup.old", "tmp/", "temp/", "uploads_old/"
        ]

    def clear_console(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def is_valid_url(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc and parsed.scheme)
    
    def extract_parameters(self, url, soup):
        parameters = {'get': {}, 'post': {}}
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        for param in query_params:
            parameters['get'][param] = query_params[param][0]
        forms = soup.find_all('form')
        for form in forms:
            form_method = form.get('method', 'get').lower()
            form_action = form.get('action', '')
            form_url = urljoin(url, form_action) if form_action else url
            form_params = {}
            for input_tag in form.find_all(['input', 'textarea', 'select']):
                input_name = input_tag.get('name')
                input_value = input_tag.get('value', '')
                if input_name:
                    form_params[input_name] = input_value
            if form_method == 'post':
                parameters['post'][form_url] = form_params
            else:
                for param_name, param_value in form_params.items():
                    parameters['get'][param_name] = param_value
        return parameters
    
    def generate_parameter_urls(self, parameters):
        parameter_urls = []
        
        for param_name, param_value in parameters['get'].items():
            test_params = parameters['get'].copy()
            test_params[param_name] = '1'
            test_url = f"{urlparse(self.target_url).scheme}://{urlparse(self.target_url).netloc}{urlparse(self.target_url).path}?{urlencode(test_params)}"
            parameter_urls.append({
                'url': test_url,
                'parameter': param_name,
                'value': '1',
                'type': 'GET'
            })
        
        for form_url, form_params in parameters['post'].items():
            for param_name, param_value in form_params.items():
                test_data = form_params.copy()
                test_data[param_name] = '1'
                parameter_urls.append({
                    'url': form_url,
                    'parameter': param_name,
                    'value': '1',
                    'type': 'POST',
                    'data': test_data
                })
        
        php_parameter_urls = self.fuzz_php_parameters()
        parameter_urls.extend(php_parameter_urls)
        
        return parameter_urls
    
    def fuzz_php_parameters(self):
        php_parameter_urls = []
        base_url = f"{urlparse(self.target_url).scheme}://{urlparse(self.target_url).netloc}"
        
        for php_file in self.common_php_files:
            for param in self.common_params:
                test_url = f"{base_url}/{php_file}?{param}=1"
                php_parameter_urls.append({
                    'url': test_url,
                    'parameter': param,
                    'value': '1',
                    'type': 'GET',
                    'source': 'fuzzing'
                })
        
        for item in self.fuzzing_items:
            if item.endswith('.php'):
                for param in self.common_params:
                    test_url = f"{base_url}/{item}?{param}=1"
                    php_parameter_urls.append({
                        'url': test_url,
                        'parameter': param,
                        'value': '1',
                        'type': 'GET',
                        'source': 'fuzzing'
                    })
        
        return php_parameter_urls
    
    def check_url_accessible(self, url):
        try:
            headers = self.headers.copy()
            headers['User-Agent'] = UserAgent().random
            response = requests.head(
                url, 
                headers=headers, 
                timeout=2,
                verify=False,
                allow_redirects=True
            )
            if response.status_code == 405:
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=2,
                    verify=False,
                    allow_redirects=True
                )
            return url, response.status_code
        except requests.exceptions.Timeout:
            return None, "TIMEOUT"
        except Exception as e:
            return None, "ERROR"
    
    def extract_links(self, url, soup):
        links = []
        try:
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                    full_url = urljoin(url, href)
                    if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                        links.append(full_url)
            
            patterns = [
                r'["\'](https?://[^"\']+)["\']',
                r'["\'](/[^"\']+)["\']',
                r'window\.location\s*=\s*["\']([^"\']+)["\']',
                r'\.href\s*=\s*["\']([^"\']+)["\']',
                r'\.open\(["\']([^"\']+)["\']',
                r'\.post\(["\']([^"\']+)["\']',
                r'\.get\(["\']([^"\']+)["\']',
                r'\.load\(["\']([^"\']+)["\']',
                r'url:\s*["\']([^"\']+)["\']',
                r'ajax\([^)]*url:\s*["\']([^"\']+)["\']',
            ]
            
            script_content = soup.find_all('script')
            for script in script_content:
                if script.string:
                    for pattern in patterns:
                        matches = re.findall(pattern, script.string)
                        for match in matches:
                            if match and not match.startswith(('javascript:', 'mailto:', 'tel:')):
                                full_url = urljoin(url, match)
                                if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                                    links.append(full_url)
        except:
            pass
        return links
    
    def crawl_page(self, url, depth=0):
        if depth > self.max_depth or url in self.visited_urls:
            return []
        self.visited_urls.add(url)
        new_links = []
        try:
            headers = self.headers.copy()
            headers['User-Agent'] = UserAgent().random
            response = requests.get(url, headers=headers, timeout=self.timeout, verify=False)
            if response.status_code == 200:
                self.valid_urls.append(url)
                print(f"{Fore.GREEN}{url} {response.status_code}")
                soup = BeautifulSoup(response.content, 'html.parser')
                page_params = self.extract_parameters(url, soup)
                if page_params['get'] or page_params['post']:
                    self.parameters_found[url] = page_params
                if depth < self.max_depth:
                    new_links = self.extract_links(url, soup)
            else:
                pass
        except Exception as e:
            pass
        return new_links
    
    def get_isp_info(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return {
                'hostname': hostname,
                'local_ip': local_ip,
                'info': 'Local Network Connection'
            }
        except:
            return {
                'hostname': 'Unknown',
                'local_ip': 'Unknown',
                'info': 'Cannot retrieve network information'
            }
    
    def start_mining(self, target_url):
        try:
            t = target_url.split('//')[1].split('/')[0]
            ip = socket.gethostbyname(t)
            country = requests.get(f'http://ip-api.com/json/{ip}', timeout=5).json().get('country', 'N/A')
        except:
            ip = "Unknown"
            country = "N/A"
        
        isp_info = self.get_isp_info()
        isp = isp_info['info']
        
        self.target_url = target_url
        self.start_time = time.time()
        self.valid_urls = []
        self.other_urls = []
        self.error_urls = []
        self.visited_urls = set()
        self.parameters_found = {}
        self.clear_console()
        print(f"""
╭────────────────────╮
│-> Minning To: {target_url}
│-> {isp} 
│-> {ip}
│-> ({country})
╰────────────────────╯

""")
        
        to_crawl = [target_url]
        
        common_paths = [
            '/admin/', '/login/', '/config/', '/user/', '/profile/', 
            '/search/', '/contact/', '/about/', '/product/', '/category/',
            '/view/', '/edit/', '/delete/', '/add/', '/upload/', '/download/',
            '/register/', '/logout/', '/cart/', '/api/', '/ajax/', '/static/',
            '/assets/', '/js/', '/css/', '/img/', '/images/', '/uploads/'
        ]
        
        for path in common_paths:
            to_crawl.append(urljoin(target_url, path))
        
        common_files = [
            'robots.txt', 'sitemap.xml', 'sitemap.txt', 'sitemap.html',
            'admin.php', 'login.php', 'config.php', 'wp-admin.php', 'wp-login.php',
            'index.php', 'index.html', 'index.jsp', 'index.aspx'
        ]
        
        for file in common_files:
            to_crawl.append(urljoin(target_url, file))
        
        current_depth = 0
        while to_crawl and current_depth <= self.max_depth:
            next_to_crawl = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                futures = {executor.submit(self.crawl_page, url, current_depth): url for url in to_crawl}
                for future in concurrent.futures.as_completed(futures):
                    try:
                        new_links = future.result(timeout=self.timeout)
                        next_to_crawl.extend(new_links)
                    except:
                        pass
            to_crawl = list(set(next_to_crawl))
            current_depth += 1
        
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        parameter_urls = {}
        if self.parameters_found:
            for url, params in self.parameters_found.items():
                parameter_urls[url] = self.generate_parameter_urls(params)
        self.show_results(elapsed_time, parameter_urls)
    
    def show_results(self, elapsed_time, parameter_urls):
        isp_info = self.get_isp_info()
        print(f"{Fore.WHITE}Target: {self.target_url}")
        print(f"{Fore.WHITE}Total URLs: {len(self.valid_urls)}")
        print(f"{Fore.GREEN}Valid URLs: {len(self.valid_urls)}")
        print(f"{Fore.WHITE}Parameters Found: {len(self.parameters_found)} URLs with parameters")
        print(f"{Fore.WHITE}Time: {elapsed_time:.2f} seconds")
        print(f"{Fore.WHITE}Hostname: {isp_info['hostname']}")
        print(f"{Fore.WHITE}Local IP: {isp_info['local_ip']}")
        print(f"{Fore.WHITE}Info: {isp_info['info']}")
        print(f"{Fore.CYAN}======================================")
        if self.parameters_found:
            for url, params in self.parameters_found.items():
                print(f"{Fore.WHITE}URL: {url}")
                if params['get']:
                    print(f"{Fore.GREEN}  GET Parameters: {', '.join(params['get'].keys())}")
                if params['post']:
                    print(f"{Fore.BLUE}  POST Forms: {len(params['post'])} forms found")
        self.show_menu(parameter_urls)
    
    def show_menu(self, parameter_urls):
        while True:
            print(f"\n{Fore.CYAN}============ OPTION MENU ============")
            print(f"{Fore.WHITE}[s] {Fore.GREEN}Save results to file")
            print(f"{Fore.WHITE}[o] {Fore.YELLOW}Show URL table")
            print(f"{Fore.WHITE}[p] {Fore.MAGENTA}Crawl parameters")
            print(f"{Fore.WHITE}[c] {Fore.BLUE}Back To Main Menu")
            print(f"{Fore.WHITE}[x] {Fore.RED}Exit program")
            print(f"{Fore.CYAN}=====================================")
            option = input(f"\n{Fore.YELLOW}Select option (s/o/p/c/x): ").lower().strip()
            if option == 's':
                self.save_results(parameter_urls)
            elif option == 'o':
                self.show_url_table()
            elif option == 'p':
                self.crawl_parameters(parameter_urls)
            elif option == 'c':
                time.sleep(2)
                self.clear_console()
                break
            elif option == 'x':
                print(f"{Fore.GREEN}Thank you! Program terminated.")
                exit()
            else:
                print(f"{Fore.RED}Invalid option! Please choose s, o, p, c, or x.")
    
    def crawl_parameters(self, parameter_urls):
        if not parameter_urls:
            print(f"{Fore.YELLOW}No parameters found to crawl!")
            return
        
        print(f"{Fore.CYAN}============ CRAWLING PARAMETERS ============")
        
        tested_urls = {}
        for url, params_list in parameter_urls.items():
            print(f"{Fore.WHITE}\nTesting parameters for: {url}")
            tested_urls[url] = []
            
            for param_info in params_list:
                test_url = param_info['url']
                param_name = param_info['parameter']
                
                try:
                    headers = self.headers.copy()
                    headers['User-Agent'] = UserAgent().random
                    
                    if param_info['type'] == 'GET':
                        response = requests.get(
                            test_url, 
                            headers=headers, 
                            timeout=2,
                            verify=False,
                            allow_redirects=True
                        )
                    else:
                        response = requests.post(
                            test_url, 
                            data=param_info.get('data', {}),
                            headers=headers, 
                            timeout=2,
                            verify=False,
                            allow_redirects=True
                        )
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        content_length = len(response.content)
                        title = soup.find('title')
                        page_title = title.get_text() if title else "No title"
                        
                        error_indicators = ['error', 'warning', 'exception', 'sql', 'syntax']
                        has_error = any(indicator in response.text.lower() for indicator in error_indicators)
                        
                        result = {
                            'parameter': param_name,
                            'status': response.status_code,
                            'content_length': content_length,
                            'has_error': has_error,
                            'title': page_title[:50] + "..." if len(page_title) > 50 else page_title
                        }
                        
                        tested_urls[url].append(result)
                        
                        status_color = Fore.GREEN if response.status_code == 200 else Fore.YELLOW
                        error_indicator = f"{Fore.RED}[ERROR]" if has_error else ""
                        
                        print(f"{status_color}  {param_name}: {response.status_code} | Size: {content_length} {error_indicator}")
                        
                    else:
                        print(f"{Fore.YELLOW}  {param_name}: {response.status_code} (Skipped)")
                        
                except Exception as e:
                    print(f"{Fore.RED}  {param_name}: Error - {str(e)}")
        
        print(f"{Fore.CYAN}\n============ CRAWLING SUMMARY ============")
        for url, results in tested_urls.items():
            if results:
                print(f"{Fore.WHITE}\nURL: {url}")
                for result in results:
                    status_color = Fore.GREEN if result['status'] == 200 else Fore.YELLOW
                    error_indicator = f"{Fore.RED} [ERROR]" if result['has_error'] else ""
                    print(f"{status_color}  {result['parameter']}: {result['status']} | {result['content_length']} chars | {result['title']}{error_indicator}")
    
    def save_results(self, parameter_urls):
        try:
            print(f"\n{Fore.CYAN}============ FILE SAVING ============")
            print(f"{Fore.WHITE}Example save locations:")
            print(f"{Fore.WHITE}- /storage/emulated/0/ (Android)")
            print(f"{Fore.WHITE}- C:\\Users\\UserName\\Documents\\ (Windows)")
            print(f"{Fore.WHITE}- /home/user_name/Documents/ (Linux)")
            print(f"{Fore.CYAN}===========================================")
            save_dir = input(f"\n{Fore.YELLOW}Enter save directory: ").strip()
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
                print(f"{Fore.GREEN}Directory created: {save_dir}")
            domain = urlparse(self.target_url).netloc.replace('www.', '')
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            mining_filename = f"{domain}_mining_results_{timestamp}.txt"
            mining_filepath = os.path.join(save_dir, mining_filename)
            with open(mining_filepath, 'w', encoding='utf-8') as f:
                f.write(f"Parameters Found: {len(self.parameters_found)} URLs with parameters\n")
                f.write(f"Mining Results for: {self.target_url}\n")
                f.write(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total URLs: {len(self.valid_urls)}\n")
                f.write(f"Green URLs (200): {len(self.valid_urls)}\n")

                f.write("=" * 60 + "\n\n")
                f.write("=== VALID URL ===\n")
                for url in self.valid_urls:
                    f.write(f"{url}\n")
                
                if self.parameters_found:
                    f.write("\n=== PARAMETERS FOUND ===\n")
                    for url, params in self.parameters_found.items():
                        f.write(f"\nURL: {url}\n")
                        if params['get']:
                            f.write("GET Parameters:\n")
                            for param_name, param_value in params['get'].items():
                                f.write(f"  {param_name} = {param_value}\n")
                        if params['post']:
                            f.write("POST Forms:\n")
                            for form_url, form_params in params['post'].items():
                                f.write(f"  Form: {form_url}\n")
                                for param_name, param_value in form_params.items():
                                    f.write(f"    {param_name} = {param_value}\n")
            print(f"{Fore.GREEN}Mining results saved to: {mining_filepath}")
            
            if parameter_urls:
                param_filename = f"{domain}_{timestamp}.txt"
                param_filepath = os.path.join(save_dir, param_filename)
                with open(param_filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Parameter URLs for: {self.target_url}\n")
                    f.write(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    for url, url_params in parameter_urls.items():
                        f.write(f"\n=== PARAMETERS FOR: {url} ===\n")
                        for i, param in enumerate(url_params, 1):
                            f.write(f"\n{i}. Parameter: {param['parameter']}\n")
                            f.write(f"   Value: {param['value']}\n")
                            f.write(f"   Type: {param['type']}\n")
                            if 'source' in param:
                                f.write(f"   Source: {param['source']}\n")
                            if param['type'] == 'GET':
                                f.write(f"   URL: {param['url']}\n")
                            else:
                                f.write(f"   URL: {param['url']}\n")
                                f.write(f"   Data: {param['data']}\n")
                print(f"{Fore.GREEN}Parameter URLs saved to: {param_filepath}")
            
            show_table = input(f"\n{Fore.YELLOW}Show results table? (y/n): ").lower().strip()
            if show_table == 'y':
                self.show_url_table()
        except Exception as e:
            print(f"{Fore.RED}Error saving file: {str(e)}")
    
    def show_url_table(self):
        total_urls = len(self.valid_urls)

        if total_urls == 0:
            print(f"{Fore.YELLOW}No URLs found!")
        else:
            self.clear_console()
            print(f"\n{Fore.GREEN}=== Valid Url ===")
            for i, url in enumerate(self.valid_urls, 1):
                print(f"{Fore.GREEN}{i:3d}. {url}")

        print(f"\n{Fore.CYAN}====================================")
        print(f"{Fore.GREEN}Green: {len(self.valid_urls)} URLs")
        print(f"{Fore.CYAN}====================================")
    
    def show_parameters(self, parameter_urls):
        if not parameter_urls:
            print(f"{Fore.YELLOW}No parameters found!")
            return
        print(f"\n{Fore.CYAN}============ PARAMETERS FOUND ============")
        for url, url_params in parameter_urls.items():
            print(f"\n{Fore.WHITE}=== URL: {url} ===")
            print(f"\n{Fore.GREEN}Parameter URLs:")
            for i, param in enumerate(url_params[:10], 1):
                print(f"{Fore.WHITE}{i}. Parameter: {Fore.CYAN}{param['parameter']}")
                print(f"   Value: {Fore.YELLOW}{param['value']}")
                print(f"   Type: {Fore.GREEN}{param['type']}")
                if 'source' in param:
                    print(f"   Source: {Fore.MAGENTA}{param['source']}")
                if param['type'] == 'GET':
                    print(f"   URL: {Fore.BLUE}{param['url']}")
                else:
                    print(f"   URL: {Fore.BLUE}{param['url']}")
                    print(f"   Data: {Fore.MAGENTA}{param['data']}")
                print()
        print(f"{Fore.CYAN}===================================================")
        print(f"{Fore.YELLOW}Note: Showing first 10 parameters only.")
        print(f"{Fore.YELLOW}Use 's' option to save all parameters.")
        print(f"{Fore.CYAN}===================================================")

def print_gradient(text, start_rgb=(0,255,0), end_rgb=(255,0,0), mode="linear"):
    length = len(text)
    
    for i, char in enumerate(text):
        if mode == "linear":
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (length-1))
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (length-1))
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (length-1))
        elif mode == "reverse":
            r = int(end_rgb[0] + (start_rgb[0] - end_rgb[0]) * i / (length-1))
            g = int(end_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (length-1))
            b = int(end_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (length-1))
        elif mode == "rainbow":
            r = int((math.sin(i / length * 2 * math.pi) + 1) * 127.5)
            g = int((math.sin(i / length * 2 * math.pi + 2*math.pi/3) + 1) * 127.5)
            b = int((math.sin(i / length * 2 * math.pi + 4*math.pi/3) + 1) * 127.5)
        else:
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (length-1))
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (length-1))
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (length-1))
        
        print(f"\033[38;2;{r};{g};{b}m{char}\033[0m", end="")
    print()

def get_github_repo_info(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return {
            'name': data.get('name', 'N/A'),
            'description': data.get('description', 'No description'),
            'stars': data.get('stargazers_count', 0),
            'forks': data.get('forks_count', 0),
            'watchers': data.get('watchers_count', 0),
            'branches': get_branch_count(owner, repo),
            'contributors': get_contributor_count(owner, repo)
        }
    else:
        print(f"Error: Unable to fetch repository data (Status code: {response.status_code})")
        return None

def get_branch_count(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/branches"
    response = requests.get(url)
    if response.status_code == 200:
        return len(response.json())
    return 0

def get_contributor_count(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(url)
    if response.status_code == 200:
        return len(response.json())
    return 0

def print_gradient_text(text, start_rgb, end_rgb):
    length = len(text)
    for i, char in enumerate(text):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (length-1))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (length-1))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (length-1))
        print(f"\033[38;2;{r};{g};{b}m{char}\033[0m", end="")

def print_boxed_table(data):
    if not data:
        return
    
    col1_width = max(len(str(key)) for key in data.keys())
    col2_width = max(len(str(value)) for value in data.values())
    
    col1_width = max(col1_width, 10)
    col2_width = max(col2_width, 10)
    
    total_width = col1_width + col2_width + 7
    
    print("┌", end="")
    print_gradient_text("─" * (col1_width + 2), (0, 255, 255), (255, 0, 255))
    print("┬", end="")
    print_gradient_text("─" * (col2_width + 2), (255, 0, 255), (0, 255, 255))
    print("┐")
    
    print("│ ", end="")
    print_gradient_text("Tools Info".ljust(col1_width), (0, 255, 255), (255, 0, 255))
    print(" │ ", end="")
    print_gradient_text("Value".ljust(col2_width), (255, 0, 255), (0, 255, 255))
    print(" │")
    
    print("├", end="")
    print_gradient_text("─" * (col1_width + 2), (0, 255, 255), (255, 0, 255))
    print("┼", end="")
    print_gradient_text("─" * (col2_width + 2), (255, 0, 255), (0, 255, 255))
    print("┤")
    
    for key, value in data.items():
        print("│ ", end="")
        print_gradient_text(str(key).ljust(col1_width), (0, 255, 255), (255, 0, 255))
        print(" │ ", end="")
        print_gradient_text(str(value).ljust(col2_width), (255, 0, 255), (0, 255, 255))
        print(" │")
    
    print("└", end="")
    print_gradient_text("─" * (col1_width + 2), (0, 255, 255), (255, 0, 255))
    print("┴", end="")
    print_gradient_text("─" * (col2_width + 2), (255, 0, 255), (0, 255, 255))
    print("┘")

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def main():
    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            owner = "REYHAN6610"
            repo = "WhaleCrusher"
            repo_info = get_github_repo_info(owner, repo)
            
            if repo_info:
                display_data = {
                    "Name": repo_info['name'],
                    "Version": "1.0",
                    "Stars": repo_info['stars'],
                    "Forks": repo_info['forks'],
                    "Watchers": repo_info['watchers'],
                    "Branches": repo_info['branches'],
                    "Contributors": repo_info['contributors']
                }
            
            print_gradient(r"""⠈⠙⠲⢶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣿⡀⠀⠀⠀⠀⠀⠀⠀⡄⠀⠀⡄⠀⠀⠀⠀⠀⠀⠀⣼⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣿⠟⠓⠉
⠀⠀⠀⠀⠈⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⢀⣧⣶⣦⣇⠀⠀⠀⠀⠀⢀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠉⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣶⣶⣶⣾⣿⣿⣿⣿⣶⣶⣶⣶⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠛⠛⠛⠛⠛⠛⠿⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠿⠟⠛⠛⠛⠛⠛⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
""", 
               start_rgb=(255, 105, 180),  # Pink hot
               end_rgb=(138, 43, 226),     # Blue violet
               mode="linear")
            print_boxed_table(display_data)
            target_url = input(f"{Fore.YELLOW}ENTER TARGET URL: ").strip()
            if target_url.lower() == 'x':
                print(f"{Fore.GREEN}Thank you! Program terminated.")
                break
            if not target_url:
                print(f"{Fore.RED}URL cannot be empty!")
                time.sleep(1)
                continue
            if not target_url.startswith(('http://', 'https://')):
                target_url = 'https://' + target_url
            miner = AdvancedWebMiner()
            miner.start_mining(target_url)
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Process terminated by user.")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}")
            time.sleep(2)

if __name__ == "__main__":
    main()