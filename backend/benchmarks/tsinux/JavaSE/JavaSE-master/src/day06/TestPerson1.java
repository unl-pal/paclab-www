package day06;

/*
 * ��ĵ�������Ա����������constructor ���췽����
 * �����������ã�
 * 1.��������
 * 2.�������Ķ�������Ը�ֵ
 * 
 * ע��
 * 1.������ʱ��������ʽ������Ĺ������Ļ��������Ĭ���ṩһ���ղεĹ�����
 * 2.һ����ʽ�Ķ�����Ĺ���������ôĬ�ϵĹ������Ͳ����ṩ
 * 3.���������Ĺ���������ʽ�� Ȩ�����η�   ����(�β�){}
 * 4.��Ķ��������֮�乹������
 */
/*
 * ���������Ը�ֵ���Ⱥ�˳��
 * 1.���Ե�Ĭ�ϳ�ʼ��
 * 2.���Ե���ʽ��ʼ��
 * 3.ͨ�������������Գ�ʼ��
 * 4.ͨ��"����.����"�ķ�ʽ�����Ը�ֵ
 * 
 */

public class TestPerson1 {
}

class Person1{
	//����
	private String name;
	private int age=1;
	
	//������   ��������
	public Person1(){
		
	}
	public Person1(int a){
		age=a;
	}
	
	public void setAge(int a){
		age=a;
	}
	
	public String getName(){
		return name;
	}
	
	public int getAge(){
		return age;
	}
	
	
}