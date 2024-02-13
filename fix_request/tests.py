from django.test import TestCase, Client
from .models import AttendanceFixRequests
from django.contrib.auth.models import User
from datetime import datetime
import json

# Create your tests here.
class AttendanceFixRequestTest(TestCase):
    fixtures = ['test_attendance_fix_records.json']
    def setUp(self):
        self.client = Client()
        self.client.login(
            username='testuser',
            password='samplesecret'
        )

    def test_not_exist_attendance_fix_request(self):
        '''
        attendancesにない打刻修正申請を行うためのテスト
        '''
        # 打刻修正のページを開く
        response = self.client.get('/fix_request/request')
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # contextの申請情報が存在しないこと
        self.assertEqual(len(response.context['fix_requests']), 0)

        # 2021/5/21の出勤打刻の修正を申請する
        response = self.client.post('/fix_request/request', {
            'push_date': '2021-05-03',
            'push_type': 'AT',
            'push_time': '9:30',
            'push_reason': 'テスト用'
        })
        # 登録されたデータを取得
        attendance_request = AttendanceFixRequests.objects.get(
            revision_time__date = datetime.strptime('2021-05-03', '%Y-%m-%d')
        )

        self.assertEqual(response.status_code, 200)
        # attendanceが空であること
        self.assertIsNone(attendance_request.attendance)

        # 打刻修正のページを開く
        response = self.client.get('/fix_request/request')
        self.assertEqual(response.status_code, 200)
        # contextの申請情報が1つ存在すること
        self.assertEqual(len(response.context['fix_requests']), 1)

    def test_exist_attendance_fix_attendanced_request(self):
        '''
        attendancesにある打刻修正申請を行うためのテスト
        '''
        # 打刻修正のページを開く
        response = self.client.get('/fix_request/request')
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # contextの申請情報が存在しないこと
        self.assertEqual(len(response.context['fix_requests']), 0)

        # 2021/5/21の退勤打刻の修正を申請する
        response = self.client.post('/fix_request/request', {
            'push_date': '2021-05-02',
            'push_type': 'LE',
            'push_time': '19:30',
            'push_reason': 'テスト用'
        })
        # 登録されたデータを取得
        attendance_request = AttendanceFixRequests.objects.get(
            revision_time__date = datetime.strptime('2021-05-02', '%Y-%m-%d')
        )

        self.assertEqual(response.status_code, 200)
        # 該当するattendancesのデータが登録されていること
        self.assertEqual(attendance_request.attendance.pk, 2)

        # 打刻修正のページを開く
        response = self.client.get('/fix_request/request')
        self.assertEqual(response.status_code, 200)
        # contextの申請情報が1つ存在すること
        self.assertEqual(len(response.context['fix_requests']), 1)

class AttendacneFixAcceptionViewTest(TestCase):
     fixtures = ['test_attendance_fix_acception.json']
     def setUp(self):
         self.client = Client()
         self.client.login(
             username='testuser',
             password='samplesecret'
         )
 
     def test_attendance_fix_request_list(self):
         '''
         打刻修正申請一覧画面を開くテスト
         '''
         # スタッフユーザーに設定する
         set_staff()
         response = self.client.get('/fix_request/acception/')
         # ステータスコードが200であること
         self.assertEqual(response.status_code, 200)
         # contextの申請情報が1つ存在すること
         self.assertEqual(len(response.context['fix_requests']), 1)
 
     def test_attendance_fix_acception_detail(self):
         '''
         存在する申請IDの詳細画面を開くテスト
         '''
         # スタッフユーザーに設定する
         set_staff()
         response = self.client.get('/fix_request/acception/detail/1')
         # ステータスコードが200で有ること
         self.assertEqual(response.status_code, 200)
         # contextの申請情報が存在すること
         self.assertIsNotNone(response.context['request_detail'])
 
     def test_invalid_user_request_list(self):
         '''
         スタッフユーザーではないユーザーが打刻修正一覧画面を開くテスト
         '''
         response = self.client.get('/fix_request/acception/')
         # ステータスコードが403であること
         self.assertEqual(response.status_code, 403)
 
     def test_invalid_user_acception_detali(self):
         '''
         スタッフユーザーではないユーザーが申請の詳細画面を開くテスト
         '''
         response = self.client.get('/fix_request/acception/detail/1')
         # ステータスコードが403であること
         self.assertEqual(response.status_code, 403)
 
 
class AcceptAttendanceFixRequestTest(TestCase):
    fixtures = ['test_attendance_fix_acception.json']
    def setUp(self):
        self.client = Client()
        self.client.login(
            username='testuser',
            password='samplesecret'
        )

    def test_accept_fix_attendance_request(self):
        '''
        申請した修正を承認するテスト
        '''
        # スタッフユーザーに設定する
        set_staff()
        # 打刻修正を承認する
        response = self.client.post('/fix_request/acception/push', {
            'result': 'accept',
            'request_id': 1
        })
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # 承認の処理が完了したレスポンスが受け取れること
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_body['result'], 'OK')
        
        # 変更したデータを取得する
        attendance_fix_request = AttendanceFixRequests.objects.get(pk=1)
        # 承認した日時が記録されていること
        self.assertIsNotNone(attendance_fix_request.checked_time)
        # is_acceptedがTrueになっていること
        self.assertTrue(attendance_fix_request.is_accepted)

    def test_reject_fix_attendance_request(self):
        '''
        申請した修正を却下するテスト
        '''
        # スタッフユーザーに設定する
        set_staff()
        # 打刻修正を承認する
        response = self.client.post('/fix_request/acception/push', {
            'result': 'reject',
            'request_id': 1
        })
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # 承認の処理が完了したレスポンスが受け取れること
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_body['result'], 'OK')

        # 変更したデータを取得する
        attendance_fix_request = AttendanceFixRequests.objects.get(pk=1)
        # 承認した日時が記録されていること
        self.assertIsNotNone(attendance_fix_request.checked_time)
        # is_acceptedがTrueになっていること
        self.assertFalse(attendance_fix_request.is_accepted)

    def test_double_push_button(self):
        '''
        ボタンを2回押したときのテスト
        '''
        # スタッフユーザーに設定する
        set_staff()
        # 打刻修正を承認する
        response = self.client.post('/fix_request/acception/push', {
            'result': 'accept',
            'request_id': 1
        })
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # 承認の処理が完了したレスポンスが受け取れること
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_body['result'], 'OK')

        # 同じ申請を却下する
        response = self.client.post('/fix_request/acception/push', {
            'result': 'reject',
            'request_id': 1
        })
        # ステータスコードが200であること
        self.assertEqual(response.status_code, 200)
        # すでに処理が完了しているレスポンスを受けとれること
        response_body = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_body['result'], 'acception_exists')

    def test_invalid_user_accept(self):
        '''
        スタッフユーザーではないユーザーが承認ボタンを押すテスト
        '''
        # 打刻修正を承認する
        response = self.client.post('/fix_request/acception/push', {
            'result': 'accept',
            'request_id': 1
        })
        # ステータスコードが403であること
        self.assertEqual(response.status_code, 403)


def set_staff():
    staff_user = User.objects.get(pk=1)
    staff_user.is_staff = True
    staff_user.save()